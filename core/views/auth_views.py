from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import LoginForm, UserRegistrationForm, VendorRegistrationForm, CollectorRegistrationForm

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
    """Customer registration with debug messages"""
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            print("Form is valid")  # Debug
            try:
                user = form.save()
                print(f"User created: {user.email}")  # Debug
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to E-RECYCLO.')
                return redirect('user_dashboard')
            except Exception as e:
                print(f"Error saving: {e}")  # Debug
                messages.error(request, f'Error: {e}')
        else:
            print("Form errors:", form.errors)  # Debug
            # Show specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/auth/register_user.html', {'form': form})

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
        form = CollectorRegistrationForm(request.POST)
        if form.is_valid():
            collector = form.save()
            login(request, collector.user)
            messages.success(request, 'Collector registration successful! You can start accepting pickups.')
            return redirect('collector_dashboard')
    else:
        form = CollectorRegistrationForm()
    
    return render(request, 'core/auth/register_collector.html', {'form': form})