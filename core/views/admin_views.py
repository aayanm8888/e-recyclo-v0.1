from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Vendor, FraudFlag, Product

def is_admin(user):
    return user.is_staff or user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Admin overview dashboard"""
    pending_vendors = Vendor.objects.filter(verification_status='pending').count()
    flagged_products = FraudFlag.objects.filter(admin_reviewed=False).count()
    total_products = Product.objects.count()
    
    context = {
        'pending_vendors': pending_vendors,
        'flagged_products': flagged_products,
        'total_products': total_products,
        'recent_flags': FraudFlag.objects.filter(admin_reviewed=False)[:5],
    }
    return render(request, 'core/admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def pending_vendors_view(request):
    """List vendors pending verification"""
    vendors = Vendor.objects.filter(verification_status='pending').order_by('-trust_score')
    return render(request, 'core/admin/pending_vendors.html', {'vendors': vendors})

@login_required
@user_passes_test(is_admin)
def verify_vendor_view(request, vendor_id):
    """Approve or reject vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            vendor.verification_status = 'approved'
            vendor.is_active = True
            messages.success(request, f'{vendor.company_name} approved successfully.')
        elif action == 'reject':
            vendor.verification_status = 'rejected'
            messages.warning(request, f'{vendor.company_name} rejected.')
        
        vendor.save()
        return redirect('pending_vendors')
    
    return render(request, 'core/admin/verify_vendor.html', {'vendor': vendor})

@login_required
@user_passes_test(is_admin)
def fraud_review_view(request):
    """Review flagged products"""
    flags = FraudFlag.objects.filter(admin_reviewed=False).order_by('-risk_score')
    return render(request, 'core/admin/fraud_review.html', {'flags': flags})

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
        flag.save()
        
        if decision == 'vendor_fraud':
            flag.product.assigned_vendor.rating -= 0.5
            flag.product.assigned_vendor.save()
            messages.error(request, 'Vendor marked as fraudulent.')
        else:
            messages.success(request, 'Dispute resolved in favor of vendor.')
        
        return redirect('fraud_review')
    
    return render(request, 'core/admin/resolve_fraud.html', {'flag': flag})