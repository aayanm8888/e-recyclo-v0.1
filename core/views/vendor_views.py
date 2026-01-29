from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Product, Vendor

@login_required
def vendor_dashboard_view(request):
    """Vendor dashboard"""
    if request.user.user_type != 'vendor':
        return redirect('user_dashboard')
    
    try:
        vendor = request.user.vendor_profile
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found.')
        return redirect('home')
    
    # Get assigned products
    pending_evaluations = Product.objects.filter(
        assigned_vendor=vendor, 
        status='delivered'
    ).order_by('-delivered_at')[:5]
    
    active_pickups = Product.objects.filter(
        assigned_vendor=vendor,
        status__in=['vendor_assigned', 'collector_assigned', 'picked_up']
    ).count()
    
    context = {
        'vendor': vendor,
        'pending_evaluations': pending_evaluations,
        'active_pickups': active_pickups,
        'total_processed': vendor.total_recycled,
        'workload_percentage': vendor.workload_percentage,
    }
    return render(request, 'core/dashboard/vendor_dashboard.html', context)

@login_required
def vendor_evaluation_view(request, product_id):
    """Vendor evaluates delivered product"""
    if request.user.user_type != 'vendor':
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, assigned_vendor=request.user.vendor_profile)
    
    if request.method == 'POST':
        # Handle evaluation submission
        declared_condition = request.POST.get('declared_condition')
        estimated_value = request.POST.get('estimated_value')
        is_recyclable = request.POST.get('is_recyclable') == 'on'
        notes = request.POST.get('notes', '')
        
        # Update product with vendor evaluation
        product.final_value = estimated_value
        product.status = 'recycled'  # or 'disputed' based on logic
        product.save()
        
        messages.success(request, 'Evaluation submitted successfully.')
        return redirect('vendor_dashboard')
    
    return render(request, 'core/vendor/evaluate_product.html', {'product': product})

@login_required
def vendor_products_view(request):
    """List all products assigned to vendor"""
    if request.user.user_type != 'vendor':
        return redirect('home')
    
    products = Product.objects.filter(assigned_vendor=request.user.vendor_profile).order_by('-uploaded_at')
    return render(request, 'core/vendor/product_list.html', {'products': products})