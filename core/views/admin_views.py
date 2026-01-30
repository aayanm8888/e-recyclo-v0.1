from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import User, Vendor, Collector, Product, FraudFlag

def is_admin(user):
    return user.is_staff or user.user_type == 'admin'


# ==================== MAIN DASHBOARD ====================

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Main admin dashboard with statistics"""
    
    # Statistics
    total_users = User.objects.count()
    total_customers = User.objects.filter(user_type='customer').count()
    total_vendors = User.objects.filter(user_type='vendor').count()
    total_collectors = User.objects.filter(user_type='collector').count()
    
    pending_vendors = Vendor.objects.filter(verification_status='pending').count()
    pending_collectors = Collector.objects.filter(verification_status='pending').count()
    
    total_products = Product.objects.count()
    pending_products = Product.objects.filter(status='pending').count()
    recycled_products = Product.objects.filter(status='recycled').count()
    
    flagged_products = FraudFlag.objects.filter(admin_reviewed=False).count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_products = Product.objects.order_by('-uploaded_at')[:5]
    
    # Revenue stats
    total_value = Product.objects.filter(final_value__isnull=False).aggregate(
        total=Sum('final_value')
    )['total'] or 0
    
    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_vendors': total_vendors,
        'total_collectors': total_collectors,
        'pending_vendors': pending_vendors,
        'pending_collectors': pending_collectors,
        'total_products': total_products,
        'pending_products': pending_products,
        'recycled_products': recycled_products,
        'flagged_products': flagged_products,
        'total_value': total_value,
        'recent_users': recent_users,
        'recent_products': recent_products,
    }
    return render(request, 'core/admin/dashboard.html', context)


# ==================== USER MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    """List all users with filters"""
    user_type = request.GET.get('type', 'all')
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if user_type != 'all':
        users = users.filter(user_type=user_type)
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'user_type': user_type,
        'search': search,
        'total_count': users.count(),
    }
    return render(request, 'core/admin/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def user_detail_view(request, user_id):
    """View user details and activity"""
    user = get_object_or_404(User, id=user_id)
    
    # Get role-specific data
    role_data = {}
    if user.user_type == 'vendor' and hasattr(user, 'vendor_profile'):
        role_data = {
            'profile': user.vendor_profile,
            'products': Product.objects.filter(assigned_vendor=user.vendor_profile).count(),
            'total_recycled': user.vendor_profile.total_recycled,
        }
    elif user.user_type == 'collector' and hasattr(user, 'collector_profile'):
        role_data = {
            'profile': user.collector_profile,
            'total_deliveries': user.collector_profile.total_deliveries,
            'rating': user.collector_profile.rating,
        }
    elif user.user_type == 'customer':
        role_data = {
            'products': Product.objects.filter(customer=user).count(),
            'wallet_balance': user.wallet_balance,
            'loyalty_points': user.loyalty_points,
        }
    
    context = {
        'user_obj': user,
        'role_data': role_data,
    }
    return render(request, 'core/admin/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def toggle_user_status_view(request, user_id):
    """Activate/Suspend user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'suspended'
        messages.success(request, f'User {user.email} has been {status}.')
    
    return redirect('user_list')


# ==================== VENDOR VERIFICATION ====================

@login_required
@user_passes_test(is_admin)
def pending_vendors_view(request):
    """List vendors pending verification"""
    vendors = Vendor.objects.filter(
        verification_status__in=['pending', 'under_review']
    ).order_by('-created_at')
    
    return render(request, 'core/admin/pending_vendors.html', {'vendors': vendors})


@login_required
@user_passes_test(is_admin)
def vendor_detail_view(request, vendor_id):
    """View vendor details and documents"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    context = {
        'vendor': vendor,
        'products_count': Product.objects.filter(assigned_vendor=vendor).count(),
    }
    return render(request, 'core/admin/vendor_detail.html', context)


@login_required
@user_passes_test(is_admin)
def verify_vendor_view(request, vendor_id):
    """Approve or reject vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            vendor.verification_status = 'approved'
            vendor.is_active = True
            vendor.license_verified = True
            vendor.save()
            messages.success(request, f'{vendor.company_name} has been approved.')
        elif action == 'reject':
            vendor.verification_status = 'rejected'
            vendor.is_active = False
            vendor.save()
            messages.warning(request, f'{vendor.company_name} has been rejected.')
        
        return redirect('pending_vendors')
    
    return render(request, 'core/admin/verify_vendor.html', {'vendor': vendor})


# ==================== COLLECTOR VERIFICATION ====================

@login_required
@user_passes_test(is_admin)
def pending_collectors_view(request):
    """List collectors pending verification"""
    collectors = Collector.objects.filter(
        verification_status__in=['pending', 'documents_pending', 'under_review']
    ).order_by('-created_at')
    
    return render(request, 'core/admin/pending_collectors.html', {'collectors': collectors})


@login_required
@user_passes_test(is_admin)
def collector_detail_view(request, collector_id):
    """View collector details and documents"""
    collector = get_object_or_404(Collector, id=collector_id)
    
    context = {
        'collector': collector,
        'is_documents_complete': collector.is_documentation_complete,
    }
    return render(request, 'core/admin/collector_detail.html', context)


@login_required
@user_passes_test(is_admin)
def verify_collector_view(request, collector_id):
    """Approve or reject collector"""
    collector = get_object_or_404(Collector, id=collector_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            collector.verification_status = 'approved'
            collector.is_verified = True
            collector.is_available = True
            collector.verified_at = timezone.now()
            collector.verified_by = request.user
            collector.save()
            messages.success(request, f'{collector.user.get_full_name()} has been approved as collector.')
        elif action == 'reject':
            collector.verification_status = 'rejected'
            collector.is_available = False
            collector.save()
            messages.warning(request, f'{collector.user.get_full_name()} has been rejected.')
        
        return redirect('pending_collectors')
    
    return render(request, 'core/admin/verify_collector.html', {'collector': collector})


# ==================== PRODUCT MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def product_list_view(request):
    """List all products with filters"""
    status = request.GET.get('status', 'all')
    
    products = Product.objects.all().order_by('-uploaded_at')
    
    if status != 'all':
        products = products.filter(status=status)
    
    context = {
        'products': products,
        'status': status,
    }
    return render(request, 'core/admin/product_list.html', context)


@login_required
@user_passes_test(is_admin)
def assign_collector_view(request, product_id):
    """Assign collector to product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        collector_id = request.POST.get('collector_id')
        collector = get_object_or_404(Collector, id=collector_id)
        
        product.assigned_collector = collector
        product.status = 'collector_assigned'
        product.assigned_at = timezone.now()
        product.save()
        
        collector.current_pickups += 1
        collector.save()
        
        messages.success(request, f'Collector {collector.user.get_full_name()} assigned successfully.')
        return redirect('admin_product_list')
    
    # Get available collectors
    available_collectors = Collector.objects.filter(
        is_verified=True,
        is_available=True,
        current_pickups__lt=3
    )
    
    context = {
        'product': product,
        'collectors': available_collectors,
    }
    return render(request, 'core/admin/assign_collector.html', context)


# ==================== FRAUD REVIEW ====================

@login_required
@user_passes_test(is_admin)
def fraud_review_view(request):
    """Review flagged products"""
    flags = FraudFlag.objects.filter(admin_reviewed=False).order_by('-risk_score')
    return render(request, 'core/admin/fraud_review.html', {'flags': flags})


@login_required
@user_passes_test(is_admin)
def fraud_detail_view(request, flag_id):
    """View fraud flag details"""
    flag = get_object_or_404(FraudFlag, id=flag_id)
    
    context = {
        'flag': flag,
        'product': flag.product,
    }
    return render(request, 'core/admin/fraud_detail.html', context)


@login_required
@user_passes_test(is_admin)
def resolve_fraud_view(request, flag_id):
    """Resolve fraud flag"""
    flag = get_object_or_404(FraudFlag, id=flag_id)
    
    if request.method == 'POST':
        decision = request.POST.get('decision')
        notes = request.POST.get('notes', '')
        
        flag.admin_decision = decision
        flag.admin_notes = notes
        flag.admin_reviewed = True
        flag.reviewed_at = timezone.now()
        flag.save()
        
        if decision == 'vendor_fraud':
            # Decrease vendor rating
            if flag.product.assigned_vendor:
                vendor = flag.product.assigned_vendor
                vendor.rating = max(0, vendor.rating - Decimal('0.5'))
                vendor.suspension_count += 1
                vendor.save()
                messages.error(request, 'Vendor marked as fraudulent. Rating decreased.')
        else:
            messages.success(request, 'Dispute resolved in favor of vendor.')
        
        return redirect('fraud_review')
    
    return render(request, 'core/admin/resolve_fraud.html', {'flag': flag})


# ==================== ANALYTICS & REPORTS ====================

@login_required
@user_passes_test(is_admin)
def analytics_view(request):
    """Analytics and reports dashboard"""
    # Date ranges
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # Product stats
    products_by_status = Product.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # User growth (last 30 days)
    user_growth = User.objects.filter(
        date_joined__date__gte=last_30_days
    ).extra(
        select={'day': 'date(date_joined)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Revenue by category
    revenue_by_category = Product.objects.filter(
        final_value__isnull=False
    ).values('category').annotate(
        total_value=Sum('final_value'),
        count=Count('id')
    ).order_by('-total_value')
    
    # Top vendors
    top_vendors = Vendor.objects.order_by('-total_recycled')[:5]
    
    # Top collectors
    top_collectors = Collector.objects.order_by('-total_deliveries')[:5]
    
    context = {
        'products_by_status': products_by_status,
        'user_growth': user_growth,
        'revenue_by_category': revenue_by_category,
        'top_vendors': top_vendors,
        'top_collectors': top_collectors,
    }
    return render(request, 'core/admin/analytics.html', context)