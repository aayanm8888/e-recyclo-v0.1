from django.urls import path
from core.views.user_views import (
    user_dashboard,
    upload_product_view,
    my_products_view
)

urlpatterns = [
    path('', user_dashboard, name='user_dashboard'),
    path('upload/', upload_product_view, name='upload_product'),
    path('my-products/', my_products_view, name='my_products'),
]