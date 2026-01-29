from django.urls import path, include

urlpatterns = [
    path('', include('core.urls.auth_urls')),
    path('dashboard/', include('core.urls.user_urls')),
    path('dashboard/vendor/', include('core.urls.vendor_urls')),
    path('dashboard/collector/', include('core.urls.collector_urls')),
    path('admin-panel/', include('core.urls.admin_urls')),  # Avoids conflict with Django admin
    path('product/', include('core.urls.product_urls')),
]