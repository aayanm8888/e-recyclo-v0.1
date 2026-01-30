from django.db import models
import uuid
from .user import User  # or however you import User

# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """
    E-Waste product uploaded by sellers for recycling
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending Pickup'),
        ('picked', 'Picked Up'),
        ('recycled', 'Recycled'),
    ]
    
    # Keep UUID as primary key to match old schema
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Product details
    name = models.CharField(max_length=200, default='Unnamed Product')
    description = models.TextField(default='No description provided')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='products'
    )
    
    # Image
    product_image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text='Upload product image'
    )
    
    # Weight for pricing/logistics
    weight_approx = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Approximate weight in kg'
    )
    
    # Seller reference (renamed from customer)
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
    )
    
    # Timestamps (renamed uploaded_at -> created_at)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.seller.username}"


class PickupRequest(models.Model):
    """
    Tracks pickup requests for e-waste products
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Keep bigint for PickupRequest (new table)
    id = models.AutoField(primary_key=True)
    
    # Link to the product (UUID foreign key)
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE,
        related_name='pickuprequest',
        help_text='The product to be picked up'
    )
    
    # Seller who requested
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pickup_requests',
        limit_choices_to={'user_type': 'seller'},
        help_text='User who requested the pickup'
    )
    
    # Collector assigned (null until assigned)
    collector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups',
        limit_choices_to={'user_type': 'collector'},
        help_text='Collector assigned to this pickup'
    )
    
    # Location Fields
    pickup_location_text = models.CharField(
        max_length=255,
        default='Address not provided'
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8,
        null=True,
        blank=True,
        help_text='Auto-detected latitude'
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8,
        null=True,
        blank=True,
        help_text='Auto-detected longitude'
    )
    
    # Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Optional notes
    seller_notes = models.TextField(blank=True)
    collector_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pickup #{self.id} - {self.product.name}"
    
    def get_location_string(self):
        if self.latitude and self.longitude:
            return f"{self.pickup_location_text} ({self.latitude}, {self.longitude})"
        return self.pickup_location_text