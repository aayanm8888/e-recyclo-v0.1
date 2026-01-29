from django.urls import path
from core.views import (
    product_detail_view,
    product_tracking_view
)

urlpatterns = [
    path('<uuid:product_id>/', product_detail_view, name='product_detail'),
    path('<uuid:product_id>/tracking/', product_tracking_view, name='product_tracking'),
]