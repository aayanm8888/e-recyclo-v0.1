from django import forms
from core.models import User, Vendor

class VendorRegistrationForm(forms.ModelForm):
    # User fields
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Vendor fields
    SPECIALIZATION_CHOICES = [
        ('smartphone', 'Smartphone'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('battery', 'Battery'),
        ('monitor', 'Monitor'),
        ('appliance', 'Appliance'),
    ]
    
    company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_document = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    gst_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    processing_capacity = forms.IntegerField(initial=100, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    specializations = forms.MultipleChoiceField(
        choices=SPECIALIZATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Vendor
        fields = ['company_name', 'license_number', 'license_document', 'gst_number', 'processing_capacity']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords don't match")
        return password2
    
    def save(self, commit=True):
        # Create User first
        user_data = {
            'email': self.cleaned_data['email'],
            'phone': self.cleaned_data['phone'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'user_type': 'vendor'
        }
        user = User(**user_data)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        
        # Create Vendor profile
        vendor = super().save(commit=False)
        vendor.user = user
        vendor.specializations = self.cleaned_data.get('specializations', [])
        if commit:
            vendor.save()
        
        return vendor