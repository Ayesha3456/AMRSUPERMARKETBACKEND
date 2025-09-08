import os
import json
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AMRSUPERMARKETBACKEND.settings")
django.setup()

from api.models import Product, Stock, Supplier, PurchaseOrder, ItemEntry, Employee, Billing, Customer, Pincode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ---------------- Helper Functions ----------------

def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {filename}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------- Import Functions ----------------

def load_suppliers():
    for item in load_json("SUPPLIER.json"):
        Supplier.objects.update_or_create(
            SUPPLIER_ID=safe_int(item.get("SUPPLIER ID")),
            defaults={
                "NAME": item.get("SUPPLIER NAME", "UNKNOWN"),
                "COMPANY_NAME": item.get("COMPANY NAME", "UNKNOWN"),
                "MOBILE_NO": item.get("MOBILE NO", "0000000000"),
                "EMAIL_ID": item.get("EMAIL ID", "unknown@example.com"),
                "CATEGORY": item.get("CATEGORY", "GENERAL")
            }
        )

def load_products():
    for item in load_json("PRODUCTWITHSTOCK.json"):
        Product.objects.update_or_create(
            id=safe_int(item.get("PRODUCTID")),
            defaults={
                "PRODUCT_NAME": item.get("PRODUCTNAME", "UNKNOWN"),
                "BRAND_NAME": item.get("BRANDNAME", "UNKNOWN"),
                "STOCK": safe_int(item.get("STOCK")),
                "MRP": float(item.get("MRP", 0)),
                "CATEGORY": item.get("CATEGORY", "GENERAL")
            }
        )

def load_stock():
    for item in load_json("STOCK.json"):
        pid = safe_int(item.get("PRODUCTID"))
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            print(f"Product {pid} not found, skipping Stock")
            continue
        Stock.objects.update_or_create(
            PRODUCT=product,
            defaults={"STOCK": safe_int(item.get("STOCK"))}
        )

def load_purchase_orders():
    for item in load_json("PURCHASEORDER.json"):
        PurchaseOrder.objects.update_or_create(
            ORDERID=safe_int(item.get("ORDERID")),
            defaults={
                "SUPPLIER_ID": safe_int(item.get("SUPPLIER ID")),
                "SUPPLIER_NAME": item.get("SUPPLIER NAME", "UNKNOWN"),
                "CATEGORY": item.get("CATEGORY", "GENERAL"),
                "PRODUCTNAME": item.get("PRODUCTNAME", "UNKNOWN"),
                "PRICE": float(item.get("PRICE", 0)),
                "QUANTITY_REQUIRED": safe_int(item.get("QUANTITY REQUIRED")),
                "TOTAL_PRICE": float(item.get("TOTAL PRICE", 0)),
                "PENDING_QUANTITY": safe_int(item.get("PENDING QUANTITY")),
                "DATE": item.get("DATE", "N/A"),
                "TIME": item.get("TIME", "N/A")
            }
        )

def load_item_entries():
    print("🗑️ Clearing old Item Entries...")
    ItemEntry.objects.all().delete()   # remove duplicates on each import

    for item in load_json("ITEMENTRY.json"):
        oid = safe_int(item.get("ORDERID"))
        try:
            order = PurchaseOrder.objects.get(ORDERID=oid)
        except PurchaseOrder.DoesNotExist:
            print(f"Order {oid} not found, skipping ItemEntry")
            continue

        ordered_qty = safe_int(item.get("ORDERED QUANTITY"))
        received_qty = safe_int(item.get("RECEIVED QUANTITY"))

        # 🔒 Cap received at ordered
        if received_qty > ordered_qty:
            received_qty = ordered_qty

        # 🔒 Ensure pending never negative
        pending_qty = max(0, ordered_qty - received_qty)

        entry = ItemEntry.objects.create(
            ORDER=order,
            SUPPLIER_NAME=item.get("SUPPLIER NAME", "UNKNOWN"),
            SUPPLIER_ID=safe_int(item.get("SUPPLIER ID")),
            PRODUCTNAME=item.get("PRODUCTNAME", "UNKNOWN"),
            CATEGORY=item.get("CATEGORY", "GENERAL"),
            RECEIVED_QUANTITY=received_qty,
            RECEIVED_DATE=parse_date(item.get("RECEIVED DATE")),
            ORDERED_QUANTITY=ordered_qty,
            PENDING_QUANTITY=pending_qty
        )

        # ✅ Sync stock (not just add blindly)
        product, _ = Product.objects.get_or_create(
            PRODUCT_NAME=item.get("PRODUCTNAME", "UNKNOWN"),
            defaults={
                "CATEGORY": item.get("CATEGORY", "GENERAL"),
                "BRAND_NAME": "UNKNOWN",
                "STOCK": 0,
                "MRP": 0
            }
        )

        stock, _ = Stock.objects.get_or_create(PRODUCT=product)
        stock.STOCK = received_qty  # set stock to received, not keep adding
        stock.save()

        print(f"✔️ ItemEntry saved: Order {oid} - {product.PRODUCT_NAME}, "
              f"Ordered={ordered_qty}, Received={received_qty}, Pending={pending_qty}")


def load_employees():
    for item in load_json("EMPLOYEE.json"):
        Employee.objects.update_or_create(
            EMPLOYEE_ID=safe_int(item.get("EMPLOYEEID")),
            defaults={
                "NAME": item.get("EMPLOYEE NAME", "UNKNOWN"),
                "MOBILE_NO": item.get("MOBILE NUMBER", "0000000000"),
                "ADDRESS": item.get("ADDRESS", "N/A"),
                "DOB": parse_date(item.get("DOB")),
                "AGE": safe_int(item.get("AGE")),
                "DOJ": parse_date(item.get("DOJ")),
                "GENDER": item.get("GENDER", "NOT_SPECIFIED"),
                "EMAIL_ID": item.get("EMAIL ID", "unknown@example.com"),
                "QUALIFICATION": item.get("QUALIFICATION", "N/A"),
                "DESIGNATION": item.get("DESIGNATION", "STAFF"),
                "BASIC_PAY": float(item.get("BASIC PAY", 0)),
                "INCENTIVE": float(item.get("INCENTIVE", 0)),
                "NET_PAY": float(item.get("NET PAY", 0))
            }
        )

def load_billing():
    for item in load_json("BILLING.json"):
        pid = safe_int(item.get("PRODUCTID"))
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            print(f"Product {pid} not found, skipping Billing")
            continue

        # ✅ Link customer if available
        cid = safe_int(item.get("CUSTOMER ID"))
        customer = None
        if cid:
            try:
                customer = Customer.objects.get(CUSTOMER_ID=cid)
            except Customer.DoesNotExist:
                pass

        Billing.objects.update_or_create(
            PRODUCT=product,
            BILL_DATE=parse_date(item.get("DATE")),
            defaults={
                "CUSTOMER": customer,
                "CATEGORY": item.get("CATEGORY", "GENERAL"),
                "QUANTITY": safe_int(item.get("QUANTITY")),
                "PRICE": float(item.get("PRICE", 0)),
                "TOTAL_PRICE": float(item.get("TOTAL PRICE", 0)),
            }
        )

def load_customers():
    for item in load_json("CUSTOMER.json"):
        Customer.objects.update_or_create(
            CUSTOMER_ID=safe_int(item.get("CUSTOMER ID")),
            defaults={
                "NAME": item.get("CUSTOMER NAME", "UNKNOWN"),
                "MOBILE_NO": item.get("MOBILE NUMBER", "0000000000"),
                "ADDRESS": item.get("ADDRESS", "N/A"),
                "CITY": item.get("CITY", "N/A"),
                "TOWN": item.get("TOWN", "N/A"),
                "PINCODE": safe_int(item.get("PINCODE"))
            }
        )

def load_pincodes():
    for item in load_json("PINCODES.json"):
        pincode = safe_int(item.get("PINCODE"))
        Pincode.objects.get_or_create(
            PINCODE=pincode,
            defaults={
                "CITY": item.get("CITY", ""),
                "STATE": item.get("STATE", ""),
                "TOWN": item.get("TOWN", "")
            }
        )

# ----------------- Run all imports -----------------

load_suppliers()
load_products()
load_stock()
load_purchase_orders()
load_item_entries()
load_employees()
load_billing()
load_customers()
load_pincodes()

print("\n✅ All data imported successfully!")
