from django.urls import path
from core.views import (
    user_dashboard_view,
    upload_product_view,
    my_products_view
)

urlpatterns = [
    path('', user_dashboard_view, name='user_dashboard'),
    path('upload/', upload_product_view, name='upload_product'),
    path('my-products/', my_products_view, name='my_products'),
]