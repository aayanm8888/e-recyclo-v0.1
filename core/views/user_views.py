from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from core.forms.product_forms import ProductUploadForm
from core.models.product import Product
from core.models.user import User  # or however your User model is imported
from core.models.product import PickupRequest

@login_required
def user_dashboard(request):
    """Seller Dashboard"""
    if request.user.user_type not in ['customer', 'seller']:
        if request.user.user_type == 'vendor':
            return redirect('vendor_dashboard')
        elif request.user.user_type == 'collector':
            return redirect('collector_dashboard')
        return redirect('home')
    
    # Profile completion calculation
    fields = [request.user.first_name, request.user.last_name, 
              request.user.phone, request.user.address, 
              request.user.profile_photo, request.user.date_of_birth]
    filled = sum(1 for f in fields if f)
    profile_completion = int((filled / len(fields)) * 100) if fields else 0
    
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.status = 'pending'
            product.save()
            
            PickupRequest.objects.create(
                product=product,
                seller=request.user,
                pickup_location_text=form.cleaned_data['pickup_location_text'],
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude'),
                status='pending'
            )
            messages.success(request, 'Product uploaded successfully!')
            return redirect('user_dashboard')
    else:
        form = ProductUploadForm()
    
    total_uploads = Product.objects.filter(seller=request.user).count()
    pending_pickups = PickupRequest.objects.filter(
        seller=request.user, status__in=['pending', 'assigned']
    ).count()
    completed_pickups = PickupRequest.objects.filter(
        seller=request.user, status='completed'
    ).count()
    recent_products = Product.objects.filter(
        seller=request.user
    ).select_related('pickuprequest').order_by('-created_at')[:4]
    
    context = {
        'upload_form': form,
        'total_uploads': total_uploads,
        'pending_pickups': pending_pickups,
        'completed_pickups': completed_pickups,
        'recent_products': recent_products,
        'profile_completion': profile_completion,
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