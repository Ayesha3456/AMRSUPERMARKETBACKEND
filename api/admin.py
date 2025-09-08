from django.contrib import admin
from .models import Product, Stock, Supplier, PurchaseOrder, ItemEntry, Billing, Employee, Customer

# ----------------- Product, Stock, Supplier, etc -----------------
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(ItemEntry)
admin.site.register(Customer)  # ✅ register Customer to manage from admin

# ----------------- Employee -----------------
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('EMPLOYEE_ID', 'NAME', 'DESIGNATION', 'MOBILE_NO', 'EMAIL_ID')
    search_fields = ('NAME', 'DESIGNATION', 'EMAIL_ID')

# ----------------- Billing -----------------
@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('BILL_NO', 'PRODUCT', 'CUSTOMER', 'EMPLOYEE', 'QUANTITY', 'TOTAL_PRICE', 'BILL_DATE')
    list_filter = ('BILL_DATE', 'EMPLOYEE', 'CUSTOMER')
    search_fields = ('PRODUCT__PRODUCT_NAME', 'CUSTOMER__NAME', 'EMPLOYEE__NAME')
