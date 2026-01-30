from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.models import Product, Collector

@login_required
def collector_dashboard_view(request):
    """Collector dashboard"""
    if request.user.user_type != 'collector':
        return redirect('user_dashboard')
    
    try:
        collector = request.user.collector_profile
    except Collector.DoesNotExist:
        messages.error(request, 'Collector profile not found.')
        return redirect('home')
    
    # Get current pickups
    current_pickups = Product.objects.filter(
        assigned_collector=collector,
        status__in=['collector_assigned', 'picked_up']
    ).order_by('-assigned_at')[:5]
    
    # Get completed deliveries
    completed_today = Product.objects.filter(
        assigned_collector=collector,
        status='delivered',
        delivered_at__date=timezone.now().date()
    ).count()
    
    context = {
        'collector': collector,
        'current_pickups': current_pickups,
        'completed_today': completed_today,
        'is_available': collector.is_available,
        'can_accept_more': collector.can_accept_more,
    }
    return render(request, 'core/dashboard/collector_dashboard.html', context)

@login_required
def mark_picked_up_view(request, product_id):
    """Mark product as picked up"""
    if request.user.user_type != 'collector':
        return redirect('home')
    
    product = get_object_or_404(
        Product, 
        id=product_id, 
        assigned_collector=request.user.collector_profile
    )
    
    product.status = 'picked_up'
    product.picked_up_at = timezone.now()
    
    # Set assigned_at if not already set
    if not product.assigned_at:
        product.assigned_at = timezone.now()
    
    product.save()
    
    messages.success(request, f'Picked up {product.category} from customer.')
    return redirect('collector_dashboard')

@login_required
def mark_delivered_view(request, product_id):
    """Mark product as delivered to vendor"""
    if request.user.user_type != 'collector':
        return redirect('home')
    
    product = get_object_or_404(
        Product,
        id=product_id,
        assigned_collector=request.user.collector_profile
    )
    
    product.status = 'delivered'
    product.delivered_at = timezone.now()
    product.save()
    
    # Update collector stats
    collector = request.user.collector_profile
    if collector.current_pickups > 0:
        collector.current_pickups -= 1
    collector.total_deliveries += 1
    collector.save()
    
    messages.success(request, f'Delivered {product.category} to vendor.')
    return redirect('collector_dashboard')

@login_required
def toggle_availability_view(request):
    """Toggle collector availability"""
    if request.user.user_type != 'collector':
        return redirect('home')
    
    collector = request.user.collector_profile
    collector.is_available = not collector.is_available
    collector.save()
    
    status = 'available' if collector.is_available else 'unavailable'
    messages.success(request, f'You are now {status} for pickups.')
    return redirect('collector_dashboard')