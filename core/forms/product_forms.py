from django import forms
from core.models.product import Product

class ProductUploadForm(forms.ModelForm):
    """Form for uploading e-waste products with location"""
    # Manual location text field
    pickup_location_text = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter complete address (e.g., 123 Main St, Mumbai)',
            'id': 'pickup-location-text'
        }),
        label='Pickup Address'
    )
    
    # Hidden lat-long fields (auto-filled by geolocation)
    latitude = forms.DecimalField(
        max_digits=10, decimal_places=8,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'latitude-field'})
    )
    longitude = forms.DecimalField(
        max_digits=11, decimal_places=8,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'longitude-field'})
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'weight_approx', 'product_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter product name (e.g., Old Refrigerator, Laptop)'
            }),
            
            'weight_approx': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Approximate weight in kg'
            }),
            'product_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'product-image'
            })
        }