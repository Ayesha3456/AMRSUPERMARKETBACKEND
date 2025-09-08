from rest_framework import serializers
from .models import Pincode, Product, Stock, Supplier, PurchaseOrder, ItemEntry, Billing, Employee, Customer

class ProductSerializer(serializers.ModelSerializer):
    PRODUCTNAME = serializers.CharField(source='PRODUCT_NAME')
    BRANDNAME = serializers.CharField(source='BRAND_NAME')

    class Meta:
        model = Product
        fields = ['id', 'PRODUCTNAME', 'BRANDNAME', 'STOCK', 'MRP', 'CATEGORY']

class StockSerializer(serializers.ModelSerializer):
    PRODUCTNAME = serializers.CharField(source='PRODUCT.PRODUCT_NAME', read_only=True)
    BRANDNAME = serializers.CharField(source='PRODUCT.BRAND_NAME', read_only=True)
    CATEGORY = serializers.CharField(source='PRODUCT.CATEGORY', read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'PRODUCT', 'PRODUCTNAME', 'BRANDNAME', 'CATEGORY', 'STOCK']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    def validate(self, data):
        supplier_id = data.get("SUPPLIER_ID")
        if not Supplier.objects.filter(SUPPLIER_ID=supplier_id).exists():
            raise serializers.ValidationError(f"Supplier {supplier_id} does not exist.")
        return data

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class ItemEntrySerializer(serializers.ModelSerializer):
    ORDERID = serializers.IntegerField(source='ORDER.ORDERID', read_only=True)
    PRICE = serializers.DecimalField(source='ORDER.PRICE', max_digits=10, decimal_places=2, read_only=True)  # 👈 add this

    class Meta:
        model = ItemEntry
        fields = [
            'id', 'ORDERID', 'ORDER', 'SUPPLIER_NAME', 'SUPPLIER_ID',
            'PRODUCTNAME', 'CATEGORY', 'RECEIVED_QUANTITY',
            'RECEIVED_DATE', 'ORDERED_QUANTITY', 'PENDING_QUANTITY', 'PRICE'
        ]

class BillingSerializer(serializers.ModelSerializer):
    PRODUCTNAME = serializers.CharField(source='PRODUCT.PRODUCT_NAME', read_only=True)
    CATEGORY = serializers.CharField(source='PRODUCT.CATEGORY', read_only=True)
    CUSTOMER_NAME = serializers.CharField(source='CUSTOMER.NAME', read_only=True)
    CUSTOMER_MOBILE = serializers.CharField(source='CUSTOMER.MOBILE_NO', read_only=True)
    EMPLOYEE_NAME = serializers.CharField(source='EMPLOYEE.NAME', read_only=True)

    class Meta:
        model = Billing
        fields = [
            'BILL_NO', 'PRODUCT', 'PRODUCTNAME', 'CATEGORY', 'QUANTITY',
            'PRICE', 'TOTAL_PRICE', 'BILL_DATE',
            'CUSTOMER', 'CUSTOMER_NAME', 'CUSTOMER_MOBILE',
            'EMPLOYEE', 'EMPLOYEE_NAME'
        ]

    def create(self, validated_data):
        product = validated_data['PRODUCT']
        quantity = validated_data['QUANTITY']

        if product.STOCK < quantity:
            raise serializers.ValidationError("Insufficient product stock.")

        # Create the billing instance
        bill = super().create(validated_data)

        # Deduct from Product main stock
        product.STOCK -= quantity
        product.save()

        remaining_qty = quantity

        # Deduct from Stock records
        stock_records = Stock.objects.filter(PRODUCT=product).order_by('id')
        for stock in stock_records:
            if remaining_qty <= 0:
                break
            if stock.STOCK >= remaining_qty:
                stock.STOCK -= remaining_qty
                remaining_qty = 0
            else:
                remaining_qty -= stock.STOCK
                stock.STOCK = 0
            stock.save()

        # ✅ Must return the created object instance
        return bill

class EmployeeSerializer(serializers.ModelSerializer):
    DOB = serializers.DateField(allow_null=True, required=False)
    DOJ = serializers.DateField(allow_null=True, required=False)
    
    class Meta:
        model = Employee
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['CUSTOMER_ID', 'NAME', 'MOBILE_NO', 'ADDRESS', 'CITY', 'TOWN', 'PINCODE']

class PincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pincode
        fields = ['PINCODE', 'CITY', 'STATE', 'TOWN']