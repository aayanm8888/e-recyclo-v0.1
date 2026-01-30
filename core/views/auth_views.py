from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth import get_user_model  # ← USE THIS
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from datetime import datetime

from core.forms import LoginForm, UserRegistrationForm, VendorRegistrationForm, CollectorRegistrationForm
from core.utils import generate_otp, send_otp_console, store_otp, verify_stored_otp

# Get User model
User = get_user_model()

def home_view(request):
    """Landing page"""
    return render(request, 'core/home.html')

def _authenticate_and_login(request, email, password, allowed_types, redirect_url, success_msg):
    """Helper function for role-based authentication"""
    user = authenticate(request, email=email, password=password)
    
    if user is None:
        messages.error(request, 'Invalid email or password.')
        return None
    
    if user.user_type not in allowed_types:
        messages.error(request, f'Access denied. This login is only for {allowed_types[0]}s.')
        return None
    
    login(request, user)
    messages.success(request, success_msg)
    return redirect(redirect_url)

# ============== SEPARATE LOGIN VIEWS ==============

def customer_login_view(request):
    """Customer-only login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            result = _authenticate_and_login(
                request, email, password,
                allowed_types=['customer'],
                redirect_url='user_dashboard',
                success_msg=f'Welcome back, {email}!'
            )
            if result:
                return result
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login_customer.html', {
        'form': form,
        'user_type': 'Customer'
    })

def vendor_login_view(request):
    """Vendor-only login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            result = _authenticate_and_login(
                request, email, password,
                allowed_types=['vendor'],
                redirect_url='vendor_dashboard',
                success_msg=f'Welcome back, Vendor {email}!'
            )
            if result:
                return result
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login_vendor.html', {
        'form': form,
        'user_type': 'Vendor'
    })

def collector_login_view(request):
    """Collector-only login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            result = _authenticate_and_login(
                request, email, password,
                allowed_types=['collector'],
                redirect_url='collector_dashboard',
                success_msg=f'Welcome back, Collector {email}!'
            )
            if result:
                return result
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login_collector.html', {
        'form': form,
        'user_type': 'Collector'
    })

def admin_login_view(request):
    """Admin/Staff-only login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is None:
                messages.error(request, 'Invalid credentials.')
            elif not user.is_staff:
                messages.error(request, 'Access denied. Staff only.')
            else:
                login(request, user)
                messages.success(request, 'Welcome to Admin Panel!')
                return redirect('admin_dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'core/auth/login_admin.html', {
        'form': form,
        'user_type': 'Administrator'
    })

def logout_view(request):
    """Logout - works for all"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# ============== REGISTRATION VIEWS (ADD THESE BACK!) ==============

def register_user_view(request):
    """Customer registration with OTP verification"""
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Store data in session (convert date to string for JSON serialization)
            cleaned_data = form.cleaned_data.copy()
            if cleaned_data.get('date_of_birth'):
                cleaned_data['date_of_birth'] = cleaned_data['date_of_birth'].isoformat()
            
            request.session['reg_data'] = cleaned_data
            request.session['reg_email'] = cleaned_data['email']
            
            # Generate and send OTP
            otp = generate_otp()
            store_otp(cleaned_data['email'], otp, timeout=600)
            send_otp_console(cleaned_data['email'], otp, "registration")
            
            messages.info(request, f'OTP sent to {cleaned_data["email"]}. Please check your console/terminal.')
            return redirect('verify_otp')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/auth/register_user.html', {'form': form})

def verify_otp_view(request):
    """Verify OTP and create user"""
    from django.contrib.auth import get_user_model
    
    if 'reg_data' not in request.session:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register_user')
    
    reg_data = request.session['reg_data']
    email = reg_data.get('email')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '')
        
        if verify_stored_otp(email, entered_otp):
            # Create user
            try:
                
                # Convert date string back to date object
                dob = None
                if reg_data.get('date_of_birth'):
                    from datetime import datetime
                    dob = datetime.fromisoformat(reg_data['date_of_birth']).date()
                
                user = User(
                    email=reg_data['email'],
                    phone=reg_data['phone'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    user_type='customer',
                    date_of_birth=dob,
                    is_active=True
                )
                user.set_password(reg_data['password1'])
                user.save()
                
                # Clear session
                del request.session['reg_data']
                if 'reg_email' in request.session:
                    del request.session['reg_email']
                
                # Auto login
                login(request, user)
                messages.success(request, 'Registration successful! Please complete your profile.')
                return redirect('user_profile')
                
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    return render(request, 'core/auth/verify_otp.html', {'email': email})

def resend_otp_view(request):
    """Resend OTP"""
    if 'reg_email' not in request.session:
        messages.error(request, 'Session expired.')
        return redirect('register_user')
    
    email = request.session['reg_email']
    otp = generate_otp()
    store_otp(email, otp, timeout=600)
    send_otp_console(email, otp, "registration")
    
    messages.info(request, 'New OTP sent. Please check console.')
    return redirect('verify_otp')

def register_vendor_view(request):
    """Vendor registration"""
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save()
            login(request, vendor.user)
            messages.success(request, 'Vendor registration submitted! Awaiting verification.')
            return redirect('vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    
    return render(request, 'core/auth/register_vendor.html', {'form': form})

def register_collector_view(request):
    """Collector registration"""
    if request.method == 'POST':
        form = CollectorRegistrationForm(request.POST, request.FILES)  # ← MUST have request.FILES!
        
        if form.is_valid():
            try:
                collector = form.save(commit=False)
                
                # Handle file uploads explicitly
                if 'profile_photo' in request.FILES:
                    collector.profile_photo = request.FILES['profile_photo']
                if 'driving_license_front' in request.FILES:
                    collector.driving_license_front = request.FILES['driving_license_front']
                if 'driving_license_back' in request.FILES:
                    collector.driving_license_back = request.FILES['driving_license_back']
                
                collector.save()
                login(request, collector.user)
                messages.success(request, 'Collector registration successful! You can start accepting pickups.')
                return redirect('collector_dashboard')
            except Exception as e:
                messages.error(request, f'Registration failed: {e}')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CollectorRegistrationForm()
    
    return render(request, 'core/auth/register_collector.html', {'form': form})