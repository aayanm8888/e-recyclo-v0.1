import uuid
from django.db import models

class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Classification'),
        ('classified', 'Classified'),
        ('vendor_assigned', 'Vendor Assigned'),
        ('collector_assigned', 'Collector Assigned'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered to Vendor'),
        ('evaluating', 'Vendor Evaluating'),
        ('recycled', 'Recycled'),
        ('disputed', 'Under Dispute'),
    ]
    
    CATEGORY_CHOICES = [
        ('smartphone', 'Smartphone'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop PC'),
        ('battery', 'Battery'),
        ('monitor', 'Monitor'),
        ('appliance', 'Appliance'),
        ('others', 'Others'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    
    image = models.ImageField(upload_to='product_images/%Y/%m/')
    pickup_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    address = models.TextField()
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    system_condition_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    assigned_vendor = models.ForeignKey(
        'Vendor', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_products'
    )
    assigned_collector = models.ForeignKey(
        'Collector', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pickups'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    system_value_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-uploaded_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return f"{self.category or 'Unknown'} - {self.customer.email}"