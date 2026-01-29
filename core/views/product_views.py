from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Product

@login_required
def product_detail_view(request, product_id):
    """View product details and tracking"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check permissions
    if request.user != product.customer and \
       request.user != product.assigned_vendor.user if product.assigned_vendor else True and \
       request.user != product.assigned_collector.user if product.assigned_collector else True and \
       not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    
    context = {
        'product': product,
        'timeline': get_product_timeline(product),
    }
    return render(request, 'core/product/detail.html', context)

def get_product_timeline(product):
    """Generate timeline of product status changes"""
    timeline = []
    
    if product.uploaded_at:
        timeline.append({'status': 'Uploaded', 'date': product.uploaded_at, 'icon': 'upload'})
    if product.status in ['classified', 'vendor_assigned', 'collector_assigned', 'picked_up', 'delivered', 'recycled']:
        timeline.append({'status': 'AI Classified', 'date': product.uploaded_at, 'icon': 'robot'})
    if product.assigned_vendor:
        timeline.append({'status': 'Vendor Assigned', 'date': product.uploaded_at, 'icon': 'store'})
    if product.assigned_collector:
        timeline.append({'status': 'Collector Assigned', 'date': product.uploaded_at, 'icon': 'truck'})
    if product.picked_up_at:
        timeline.append({'status': 'Picked Up', 'date': product.picked_up_at, 'icon': 'check'})
    if product.delivered_at:
        timeline.append({'status': 'Delivered to Vendor', 'date': product.delivered_at, 'icon': 'building'})
    if product.status == 'recycled':
        timeline.append({'status': 'Recycled', 'date': product.completed_at or product.delivered_at, 'icon': 'recycle'})
    
    return timeline

@login_required
def product_tracking_view(request, product_id):
    """Public tracking view for customers"""
    product = get_object_or_404(Product, id=product_id)
    
    # Only customer can view their own tracking (or admin)
    if request.user != product.customer and not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    
    return render(request, 'core/product/tracking.html', {'product': product})