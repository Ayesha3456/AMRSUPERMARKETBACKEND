from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'stock', StockViewSet)
router.register(r'supplier', SupplierViewSet)
router.register(r'purchaseorder', PurchaseOrderViewSet)
router.register(r'itementry', ItemEntryViewSet)
router.register(r'billing', BillingViewSet)
router.register(r'employee', EmployeeViewSet, basename='employee')
router.register(r'customer', CustomerViewSet)
router.register(r'pincode', PincodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
