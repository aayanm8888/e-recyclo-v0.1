from django import forms
from core.models import Product

class ProductUploadForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'  # For mobile camera
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Pickup address',
            'rows': 3
        })
    )
    latitude = forms.DecimalField(
        widget=forms.HiddenInput(),
        required=False
    )
    longitude = forms.DecimalField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['image', 'address', 'latitude', 'longitude']
    
    def save(self, customer, commit=True):
        product = super().save(commit=False)
        product.customer = customer
        product.status = 'pending'
        if commit:
            product.save()
        return product