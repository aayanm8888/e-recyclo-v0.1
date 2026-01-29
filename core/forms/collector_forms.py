from django import forms
from django.core.validators import RegexValidator
from core.models import User, Collector

class CollectorRegistrationForm(forms.ModelForm):
    # User fields
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    phone_regex = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Enter valid 10-digit Indian mobile number"
    )
    phone = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Collector fields
    VEHICLE_CHOICES = [
        ('bike', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('van', 'Van'),
    ]
    
    vehicle_type = forms.ChoiceField(
        choices=VEHICLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vehicle_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., MH01AB1234 (Required for Bike/Van)'
        })
    )
    driving_license_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., MH0120230001234'
        })
    )
    
    # Documents
    profile_photo = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Clear passport-size photo for ID"
    )
    driving_license_front = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label="Driving License (Front)"
    )
    driving_license_back = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label="Driving License (Back)"
    )
    vehicle_registration = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label="Vehicle Registration Certificate (Optional)"
    )
    
    # Emergency contact
    emergency_contact_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emergency_contact_phone = forms.CharField(
        required=False,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Service area
    service_area = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Areas you can serve (e.g., Andheri, Bandra, Dadar)'
        })
    )
    
    class Meta:
        model = Collector
        fields = ['vehicle_type', 'vehicle_number', 'driving_license_number']
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        
        # Validate vehicle number for bike/van
        vehicle_type = cleaned_data.get('vehicle_type')
        vehicle_number = cleaned_data.get('vehicle_number')
        
        if vehicle_type in ['bike', 'van'] and not vehicle_number:
            raise forms.ValidationError("Vehicle number is required for Bike/Van")
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create User
        user_data = {
            'email': self.cleaned_data['email'],
            'phone': self.cleaned_data['phone'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'user_type': 'collector'
        }
        user = User(**user_data)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        
        # Create Collector (not available until verified)
        collector = super().save(commit=False)
        collector.user = user
        collector.is_available = False  # Must be verified first
        collector.verification_status = 'pending'
        
        if commit:
            collector.save()
        
        return collector