from django.urls import path
from core.views import (
    vendor_dashboard_view,
    vendor_evaluation_view,
    vendor_products_view
)

urlpatterns = [
    path('', vendor_dashboard_view, name='vendor_dashboard'),
    path('products/', vendor_products_view, name='vendor_products'),
    path('evaluate/<uuid:product_id>/', vendor_evaluation_view, name='vendor_evaluation'),
]