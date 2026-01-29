from django.urls import path
from core.views import (
    collector_dashboard_view,
    mark_picked_up_view,
    mark_delivered_view,
    toggle_availability_view
)

urlpatterns = [
    path('', collector_dashboard_view, name='collector_dashboard'),
    path('toggle-availability/', toggle_availability_view, name='toggle_availability'),
    path('pickup/<uuid:product_id>/', mark_picked_up_view, name='mark_picked_up'),
    path('deliver/<uuid:product_id>/', mark_delivered_view, name='mark_delivered'),
]