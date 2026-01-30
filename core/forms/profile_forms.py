from django import forms
from core.models import User, Collector, Vendor
from core.validators import validate_indian_mobile, validate_pincode

class UserProfileForm(forms.ModelForm):
    """Form for customers to complete their profile"""
    
    # Optional fields that contribute to completion percentage
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    phone = forms.CharField(
        validators=[validate_indian_mobile],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit mobile number'
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Full address (street, building, area)',
            'rows': 3
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State'
        })
    )
    
    pincode = forms.CharField(
        required=False,
        validators=[validate_pincode],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '6-digit pincode',
            'maxlength': '6'
        })
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = User
        fields = ['profile_photo', 'first_name', 'last_name', 'phone', 
                  'date_of_birth', 'address', 'city', 'state', 'pincode']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email read-only
        if self.instance and self.instance.pk:
            self.fields['email'] = forms.EmailField(
                initial=self.instance.email,
                disabled=True,
                widget=forms.EmailInput(attrs={'class': 'form-control'})
            )
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Check if phone changed and if new phone already exists
            if self.instance and self.instance.phone != phone:
                if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("This phone number is already registered.")
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Recalculate completion
            user.calculate_profile_completion()
        return user


class PasswordChangeForm(forms.Form):
    """Password change form for all user types"""
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password (min 8 chars)'
        }),
        min_length=8,
        help_text="Must be at least 8 characters"
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Current password is incorrect.')
        return old_password
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("New passwords do not match.")
        return password2
    
    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user