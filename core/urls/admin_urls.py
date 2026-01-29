from django.urls import path
from core.views import (
    admin_dashboard_view,
    pending_vendors_view,
    verify_vendor_view,
    fraud_review_view,
    resolve_fraud_view
)

urlpatterns = [
    path('', admin_dashboard_view, name='admin_dashboard'),
    path('pending-vendors/', pending_vendors_view, name='pending_vendors'),
    path('verify-vendor/<uuid:vendor_id>/', verify_vendor_view, name='verify_vendor'),
    path('fraud-review/', fraud_review_view, name='fraud_review'),
    path('resolve-fraud/<uuid:flag_id>/', resolve_fraud_view, name='resolve_fraud'),
]