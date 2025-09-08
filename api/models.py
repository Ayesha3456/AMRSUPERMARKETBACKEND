from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    CATEGORY = models.CharField(max_length=50, default='GENERAL', db_column='CATEGORY')
    PRODUCT_NAME = models.CharField(max_length=100, default='UNKNOWN', db_column='PRODUCTNAME')
    BRAND_NAME = models.CharField(max_length=100, default='UNKNOWN', db_column='BRANDNAME')
    STOCK = models.IntegerField(default=0, db_column='STOCK')
    MRP = models.FloatField(default=0.0, db_column='MRP')

    def __str__(self):
        return self.PRODUCT_NAME

class Stock(models.Model):
    PRODUCT = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='STOCK_RECORD', db_column='PRODUCTID')
    STOCK = models.IntegerField(default=0, db_column='STOCK')

    def __str__(self):
        return f"{self.PRODUCT.PRODUCT_NAME} - {self.STOCK}"

class Supplier(models.Model):
    SUPPLIER_ID = models.AutoField(primary_key=True, db_column='SUPPLIERID')
    NAME = models.CharField(max_length=100, db_column='SUPPLIERNAME', default='UNKNOWN')
    COMPANY_NAME = models.CharField(max_length=100, db_column='COMPANYNAME', default='UNKNOWN')
    MOBILE_NO = models.CharField(max_length=15, db_column='MOBILENO', default='0000000000')
    EMAIL_ID = models.EmailField(db_column='EMAILID', default='unknown@example.com')
    CATEGORY = models.CharField(max_length=50, db_column='CATEGORY', default='GENERAL')

    def __str__(self):
        return self.NAME

class PurchaseOrder(models.Model):
    ORDERID = models.AutoField(primary_key=True)
    SUPPLIER_ID = models.IntegerField(db_column="SUPPLIER_ID", default=0)
    SUPPLIER_NAME = models.CharField(max_length=100, db_column="SUPPLIER_NAME", default='UNKNOWN')
    CATEGORY = models.CharField(max_length=100, default="GENERAL")
    PRODUCTNAME = models.CharField(max_length=100, default="UNKNOWN")
    PRICE = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    QUANTITY_REQUIRED = models.IntegerField(default=0)
    TOTAL_PRICE = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    DATE = models.CharField(max_length=50, default="N/A")
    TIME = models.CharField(max_length=50, default="N/A")
    PENDING_QUANTITY = models.IntegerField(default=0)

    def __str__(self):
        return f"Order {self.ORDERID}"

class ItemEntry(models.Model):
    ORDER = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, db_column='ORDERID', related_name='ITEMENTRIES')
    SUPPLIER_NAME = models.CharField(max_length=100, db_column="SUPPLIERNAME", default='UNKNOWN')
    SUPPLIER_ID = models.IntegerField(db_column="SUPPLIERID", default=0)
    PRODUCTNAME = models.CharField(max_length=100, db_column="PRODUCTNAME", default='UNKNOWN')
    CATEGORY = models.CharField(max_length=100, default="GENERAL", db_column="CATEGORY")
    RECEIVED_QUANTITY = models.IntegerField(default=0, db_column='RECEIVEDQUANTITY')
    RECEIVED_DATE = models.DateField(db_column='RECEIVEDDATE', null=True, blank=True)
    ORDERED_QUANTITY = models.IntegerField(default=0, db_column='ORDEREDQUANTITY')
    PENDING_QUANTITY = models.IntegerField(default=0, db_column='PENDINGQUANTITY')

    def __str__(self):
        return f"Item Entry for Order {self.ORDER.ORDERID} - {self.PRODUCTNAME}"


class Customer(models.Model):
    CUSTOMER_ID = models.AutoField(primary_key=True, db_column='CUSTOMERID')
    NAME = models.CharField(max_length=100, db_column='CUSTOMERNAME', default='UNKNOWN')
    MOBILE_NO = models.CharField(max_length=15, db_column='MOBILE', default='0000000000')
    ADDRESS = models.TextField(db_column='ADDRESS', default='N/A')
    CITY = models.CharField(max_length=50, db_column='CITY', default='N/A')
    TOWN = models.CharField(max_length=50, db_column='TOWN', default='N/A')
    PINCODE = models.IntegerField(db_column='PINCODE', default=0)

    def __str__(self):
        return self.NAME


class Billing(models.Model):
    BILL_NO = models.AutoField(primary_key=True, db_column='BILLNO')
    PRODUCT = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='PRODUCTID')
    CUSTOMER = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, db_column='CUSTOMERID')
    EMPLOYEE = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, db_column='EMPLOYEEID')  # ✅ new
    CATEGORY = models.CharField(max_length=50, default='GENERAL', db_column='CATEGORY')
    QUANTITY = models.IntegerField(default=0, db_column='QUANTITY')
    PRICE = models.FloatField(default=0.0, db_column='PRICE')
    TOTAL_PRICE = models.FloatField(default=0.0, db_column='TOTALPRICE')
    BILL_DATE = models.DateField(null=True, blank=True, db_column='BILLDATE')

    def __str__(self):
        return f"Bill {self.BILL_NO}"


class Employee(models.Model):
    EMPLOYEE_ID = models.AutoField(primary_key=True, db_column='EMPLOYEEID')
    NAME = models.CharField(max_length=100, default='UNKNOWN', db_column='EMPLOYEENAME')
    MOBILE_NO = models.CharField(max_length=15, default='0000000000', db_column='MOBILENO')
    ADDRESS = models.TextField(default='N/A', db_column='ADDRESS')
    DOB = models.DateField(db_column='DOB', null=True, blank=True)
    AGE = models.IntegerField(default=0, db_column='AGE')
    DOJ = models.DateField(db_column='DOJ', null=True, blank=True)
    GENDER = models.CharField(max_length=10, default='NOT_SPECIFIED', db_column='GENDER')
    EMAIL_ID = models.EmailField(default='unknown@example.com', db_column='EMAILID')
    QUALIFICATION = models.CharField(max_length=100, default='N/A', db_column='QUALIFICATION')
    DESIGNATION = models.CharField(max_length=100, default='STAFF', db_column='DESIGNATION')
    BASIC_PAY = models.FloatField(default=0.0, db_column='BASICPAY')
    INCENTIVE = models.FloatField(default=0.0, db_column='INCENTIVE')
    NET_PAY = models.FloatField(default=0.0, db_column='NETPAY')

    def __str__(self):
        return self.NAME

class Pincode(models.Model):
    PINCODE = models.IntegerField(unique=True)
    CITY = models.CharField(max_length=100, blank=True)
    STATE = models.CharField(max_length=100, blank=True)
    TOWN = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.PINCODE)
