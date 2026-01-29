import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Vendor(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'User', 
        on_delete=models.CASCADE, 
        related_name='vendor_profile'
    )
    
    company_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100, unique=True)
    license_document = models.FileField(upload_to='vendor_licenses/%Y/%m/')
    license_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='pending'
    )
    trust_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    ocr_data = models.JSONField(default=dict, blank=True)
    forensics_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    gst_number = models.CharField(max_length=15, blank=True)
    specializations = models.JSONField(default=list)
    processing_capacity = models.IntegerField(default=100)
    current_workload = models.IntegerField(default=0)
    
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=5.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_recycled = models.IntegerField(default=0)
    successful_evaluations = models.IntegerField(default=0)
    disputed_evaluations = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    suspension_count = models.IntegerField(default=0)
    last_suspension_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendors'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        indexes = [
            models.Index(fields=['verification_status', 'trust_score']),
            models.Index(fields=['is_active', 'rating']),
        ]
    
    def __str__(self):
        return f"{self.company_name} ({self.license_number})"
    
    @property
    def workload_percentage(self):
        if self.processing_capacity <= 0:
            return 0
        return (self.current_workload / self.processing_capacity) * 100
    
    @property
    def can_accept_work(self):
        return (
            self.is_active and 
            self.verification_status == 'approved' and
            self.workload_percentage < 90
        )