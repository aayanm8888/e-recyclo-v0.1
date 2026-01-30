from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from core.forms.profile_forms import UserProfileForm, PasswordChangeForm
from core.models import User

@login_required
def user_profile_view(request):
    """Customer profile view - edit profile and see completion"""
    if request.user.user_type != 'customer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            completion = user.profile_completion
            messages.success(request, f'Profile updated successfully! ({completion}% complete)')
            
            if user.profile_complete:
                messages.success(request, 'Your profile is now complete! You can start uploading e-waste items.')
            
            return redirect('user_profile')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    else:
        form = UserProfileForm(instance=user)
    
    # Calculate current completion
    completion = user.calculate_profile_completion()
    missing_fields = []
    
    # Check what's missing
    if not user.profile_photo:
        missing_fields.append("Profile Photo")
    if not user.date_of_birth:
        missing_fields.append("Date of Birth")
    if not user.address:
        missing_fields.append("Address")
    if not user.city:
        missing_fields.append("City")
    if not user.state:
        missing_fields.append("State")
    if not user.pincode:
        missing_fields.append("Pincode")
    
    context = {
        'form': form,
        'user_obj': user,
        'completion': completion,
        'is_complete': user.profile_complete,
        'missing_fields': missing_fields,
        'can_upload': completion >= 50,  # Allow upload at 50%
    }
    return render(request, 'core/profile/user_profile.html', context)

@login_required
def password_change_view(request):
    """Password change for all users"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Keep user logged in
            messages.success(request, 'Password changed successfully!')
            return redirect('user_profile')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/profile/password_change.html', {'form': form})


def password_reset_request_view(request):
    """Request password reset - sends OTP to console"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
            from core.utils import generate_otp, send_otp_console, store_otp
            
            otp = generate_otp()
            store_otp(email, otp, timeout=600)  # 10 minutes
            
            send_otp_console(email, otp, "password reset")
            
            request.session['pwd_reset_email'] = email
            messages.info(request, f'OTP sent to {email}. Check your console/terminal.')
            return redirect('password_reset_verify')
            
        except User.DoesNotExist:
            # Don't reveal if email exists
            messages.info(request, f'If an account exists with {email}, an OTP has been sent.')
            return redirect('password_reset')
    
    return render(request, 'core/auth/password_reset_request.html')


def password_reset_verify_view(request):
    """Verify OTP and set new password"""
    if request.user.is_authenticated:
        return redirect('home')
    
    email = request.session.get('pwd_reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request OTP again.')
        return redirect('password_reset')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            from core.utils import verify_stored_otp
            
            if verify_stored_otp(email, otp):
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    
                    # Clear session
                    if 'pwd_reset_email' in request.session:
                        del request.session['pwd_reset_email']
                    
                    messages.success(request, 'Password reset successful! Please login.')
                    return redirect('login_customer')
                except User.DoesNotExist:
                    pass
            
            messages.error(request, 'Invalid or expired OTP.')
    
    return render(request, 'core/auth/password_reset_verify.html')