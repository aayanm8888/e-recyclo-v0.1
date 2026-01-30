import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

def validate_indian_mobile(value):
    """Validate 10-digit Indian mobile number"""
    if not value:
        return value
    
    pattern = r'^[6-9]\d{9}$'
    if not re.match(pattern, str(value)):
        raise ValidationError('Enter a valid 10-digit Indian mobile number starting with 6-9.')
    return value

def validate_adult_dob(value):
    """Validate user is at least 18 years old"""
    if not value:
        raise ValidationError('Date of birth is required.')
    
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    
    if age < 18:
        raise ValidationError('You must be at least 18 years old to register.')
    if age > 100:
        raise ValidationError('Please enter a valid date of birth.')
    return value

def validate_vehicle_number(value):
    """Validate Indian vehicle registration number"""
    if not value:
        return value
    
    # Format: MH01AB1234, MH 01 AB 1234, MH-01-AB-1234 (case insensitive)
    pattern = r'^[A-Z]{2}\s*[-]?\s*[0-9]{1,2}\s*[-]?\s*[A-Z]{0,2}\s*[-]?\s*[0-9]{1,4}$'
    if not re.match(pattern, str(value), re.IGNORECASE):
        raise ValidationError('Enter a valid vehicle number (e.g., MH01AB1234 or MH-01-AB-1234)')
    return value.upper()

def validate_driving_license(value):
    """Validate Indian driving license number"""
    if not value:
        return value
    
    # Format: MH0120230001234 (2 letters + 13-15 digits)
    pattern = r'^[A-Z]{2}\d{13,15}$'
    if not re.match(pattern, str(value).upper()):
        raise ValidationError('Enter a valid driving license number (e.g., MH0120230001234)')
    return value.upper()

def validate_gstin(value):
    """Validate 15-character GSTIN"""
    if not value:
        return value
    
    if len(str(value)) != 15:
        raise ValidationError('GSTIN must be exactly 15 characters.')
    
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, str(value).upper()):
        raise ValidationError('Enter a valid GSTIN (e.g., 27AAPFU0939F1ZV)')
    return value.upper()

def validate_pincode(value):
    """Validate 6-digit Indian pincode"""
    if not value:
        return value
    
    pattern = r'^\d{6}$'
    if not re.match(pattern, str(value)):
        raise ValidationError('Enter a valid 6-digit pincode.')
    return value