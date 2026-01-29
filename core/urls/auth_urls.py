from django.urls import path
from core.views import auth_views

urlpatterns = [
    path('', auth_views.home_view, name='home'),
    
    # Separate Login URLs
    path('login/user/', auth_views.customer_login_view, name='login_customer'),
    path('login/vendor/', auth_views.vendor_login_view, name='login_vendor'),
    path('login/collector/', auth_views.collector_login_view, name='login_collector'),
    path('login/admin/', auth_views.admin_login_view, name='login_admin'),
    
    path('logout/', auth_views.logout_view, name='logout'),
    
    # Registrations remain separate
    path('register/', auth_views.register_user_view, name='register_user'),
    path('register/vendor/', auth_views.register_vendor_view, name='register_vendor'),
    path('register/collector/', auth_views.register_collector_view, name='register_collector'),
]