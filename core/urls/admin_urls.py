from django.urls import path
from core.views import admin_views

urlpatterns = [
    # Main Dashboard
    path('', admin_views.admin_dashboard_view, name='admin_dashboard'),
    
    # User Management
    path('users/', admin_views.user_list_view, name='user_list'),
    path('users/<uuid:user_id>/', admin_views.user_detail_view, name='user_detail'),
    path('users/<uuid:user_id>/toggle/', admin_views.toggle_user_status_view, name='toggle_user_status'),
    
    # Vendor Verification
    path('pending-vendors/', admin_views.pending_vendors_view, name='pending_vendors'),
    path('vendors/<uuid:vendor_id>/', admin_views.vendor_detail_view, name='vendor_detail'),
    path('verify-vendor/<uuid:vendor_id>/', admin_views.verify_vendor_view, name='verify_vendor'),
    
    # Collector Verification (NEW!)
    path('pending-collectors/', admin_views.pending_collectors_view, name='pending_collectors'),
    path('collectors/<uuid:collector_id>/', admin_views.collector_detail_view, name='collector_detail'),
    path('verify-collector/<uuid:collector_id>/', admin_views.verify_collector_view, name='verify_collector'),
    
    # Product Management
    path('products/', admin_views.product_list_view, name='admin_product_list'),
    path('products/<uuid:product_id>/assign/', admin_views.assign_collector_view, name='assign_collector'),
    
    # Fraud Review
    path('fraud-review/', admin_views.fraud_review_view, name='fraud_review'),
    path('fraud-review/<uuid:flag_id>/', admin_views.fraud_detail_view, name='fraud_detail'),
    path('resolve-fraud/<uuid:flag_id>/', admin_views.resolve_fraud_view, name='resolve_fraud'),
    
    # Analytics
    path('analytics/', admin_views.analytics_view, name='admin_analytics'),
]