import random
import string
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def generate_otp(length=6):
    """Generate numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_console(email, otp, purpose="verification"):
    """Send OTP to console (for development)"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print("\n" + "="*60)
    print(f"📧 EMAIL NOTIFICATION [{timestamp}]")
    print("="*60)
    print(f"To: {email}")
    print(f"Subject: E-RECYCLO - {purpose.title()} OTP")
    print("-"*60)
    print(f"Hello,")
    print(f"")
    print(f"Your One-Time Password (OTP) for {purpose} is:")
    print(f"")
    print(f"    🔢 {otp}")
    print(f"")
    print(f"This OTP is valid for 10 minutes.")
    print(f"Do not share this code with anyone.")
    print("="*60 + "\n")
    
    # Also try Django email (will use console backend during dev)
    try:
        send_mail(
            subject=f'E-RECYCLO - {purpose.title()} OTP',
            message=f'Your OTP is: {otp}\nValid for 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True
        )
    except:
        pass
    
    return otp

def store_otp(email, otp, timeout=600):
    """Store OTP in cache"""
    cache_key = f'otp_{email}'
    cache.set(cache_key, otp, timeout)
    return True

def verify_stored_otp(email, otp):
    """Verify OTP from cache"""
    cache_key = f'otp_{email}'
    stored_otp = cache.get(cache_key)
    
    if stored_otp and str(stored_otp) == str(otp):
        # Delete after successful verification
        cache.delete(cache_key)
        return True
    return False

def get_remaining_otp_time(email):
    """Get remaining time for OTP in seconds"""
    cache_key = f'otp_{email}'
    # Django cache doesn't expose TTL directly, so we check if exists
    if cache.get(cache_key):
        return True
    return False