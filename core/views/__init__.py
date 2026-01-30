# Auth views
from .auth_views import (
    home_view,
    customer_login_view,
    vendor_login_view,
    collector_login_view,
    admin_login_view,
    logout_view,
    register_user_view,
    register_vendor_view,
    register_collector_view
)

# User views
from .user_views import (
    user_dashboard,
    upload_product_view,
    my_products_view
)

# Vendor views
from .vendor_views import (
    vendor_dashboard_view,
    vendor_evaluation_view,
    vendor_products_view
)

# Collector views
from .collector_views import (
    collector_dashboard_view,
    mark_picked_up_view,
    mark_delivered_view,
    toggle_availability_view
)

# Admin views
from .admin_views import (
    admin_dashboard_view,
    pending_vendors_view,
    verify_vendor_view,
    fraud_review_view,
    resolve_fraud_view
)

# Product views
from .product_views import (
    product_detail_view,
    product_tracking_view
)

__all__ = [
    # Auth
    'home_view',
    'customer_login_view',
    'vendor_login_view', 
    'collector_login_view',
    'admin_login_view',
    'logout_view',
    'register_user_view',
    'register_vendor_view',
    'register_collector_view',
    # User
    'user_dashboard_view',
    'upload_product_view',
    'my_products_view',
    # Vendor
    'vendor_dashboard_view',
    'vendor_evaluation_view',
    'vendor_products_view',
    # Collector
    'collector_dashboard_view',
    'mark_picked_up_view',
    'mark_delivered_view',
    'toggle_availability_view',
    # Admin
    'admin_dashboard_view',
    'pending_vendors_view',
    'verify_vendor_view',
    'fraud_review_view',
    'resolve_fraud_view',
    # Product
    'product_detail_view',
    'product_tracking_view',
]