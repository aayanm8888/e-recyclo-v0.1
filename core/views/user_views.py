from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Product
from core.forms import ProductUploadForm

@login_required
def user_dashboard_view(request):
    """Customer dashboard"""
    if request.user.user_type != 'customer':
        return redirect('vendor_dashboard' if request.user.user_type == 'vendor' else 'collector_dashboard')
    
    # Get user's products
    products = Product.objects.filter(customer=request.user).order_by('-uploaded_at')[:10]
    
    context = {
        'products': products,
        'total_products': Product.objects.filter(customer=request.user).count(),
        'recycled_count': Product.objects.filter(customer=request.user, status='recycled').count(),
        'wallet_balance': request.user.wallet_balance,
        'loyalty_points': request.user.loyalty_points,
    }
    return render(request, 'core/dashboard/user_dashboard.html', context)

@login_required
def upload_product_view(request):
    """Upload new e-waste item"""
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can upload products.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(customer=request.user)
            messages.success(request, 'Product uploaded successfully! AI classification in progress...')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductUploadForm()
    
    return render(request, 'core/product/upload_product.html', {'form': form})

@login_required
def my_products_view(request):
    """List all user products"""
    if request.user.user_type != 'customer':
        return redirect('home')
    
    products = Product.objects.filter(customer=request.user).order_by('-uploaded_at')
    return render(request, 'core/product/my_products.html', {'products': products})