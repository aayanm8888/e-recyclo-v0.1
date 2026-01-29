import uuid
from django.db import models

class Collector(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('documents_pending', 'Documents Required'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    VEHICLE_CHOICES = [
        ('bicycle', 'Bicycle'),
        ('bike', 'Motorcycle'),
        ('van', 'Van'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'User', 
        on_delete=models.CASCADE, 
        related_name='collector_profile'
    )
    
    # ========== VERIFICATION SYSTEM ==========
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='pending'
    )
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_collectors'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # ========== DOCUMENTS ==========
    profile_photo = models.ImageField(
        upload_to='collectors/photos/%Y/%m/',
        help_text="Clear face photo for identification"
    )
    driving_license_front = models.ImageField(
        upload_to='collectors/licenses/%Y/%m/',
        verbose_name="DL Front"
    )
    driving_license_back = models.ImageField(
        upload_to='collectors/licenses/%Y/%m/',
        verbose_name="DL Back"
    )
    vehicle_registration = models.ImageField(
        upload_to='collectors/vehicle_docs/%Y/%m/',
        blank=True, 
        null=True
    )
    police_verification_doc = models.FileField(
        upload_to='collectors/police_verification/%Y/%m/',
        blank=True,
        null=True,
        help_text="Optional: Police clearance certificate"
    )
    
    # ========== VEHICLE DETAILS ==========
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_CHOICES, 
        default='bike'
    )
    vehicle_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="License plate number"
    )
    driving_license_number = models.CharField(
        max_length=20,
        blank=True
    )
    license_expiry_date = models.DateField(null=True, blank=True)
    
    # ========== AVAILABILITY & WORK ==========
    is_available = models.BooleanField(default=False)  # False until verified!
    current_pickups = models.IntegerField(default=0)
    total_deliveries = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    
    # ========== SAFETY & PERFORMANCE ==========
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=10, blank=True)
    
    # Flags
    incident_count = models.IntegerField(default=0)
    customer_complaints = models.IntegerField(default=0)
    last_incident_date = models.DateTimeField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    
    # ========== ASSIGNMENT ==========
    permanent_vendor = models.ForeignKey(
        'Vendor', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='permanent_collectors'
    )
    service_area = models.CharField(
        max_length=200,
        blank=True,
        help_text="Preferred service areas/localities"
    )
    
    # ========== TIMESTAMPS ==========
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collectors'
        verbose_name = 'Collector'
        verbose_name_plural = 'Collectors'
        indexes = [
            models.Index(fields=['verification_status', 'is_available']),
            models.Index(fields=['vehicle_type', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_vehicle_type_display()}) - {self.get_verification_status_display()}"
    
    @property
    def can_accept_more(self):
        """Max 3 concurrent pickups"""
        return self.current_pickups < 3
    
    @property
    def is_documentation_complete(self):
        """Check if all required docs uploaded"""
        return all([
            self.profile_photo,
            self.driving_license_front,
            self.driving_license_back,
            self.driving_license_number,
            self.vehicle_number if self.vehicle_type in ['bike', 'van'] else True
        ])
    
    @property
    def vehicle_display(self):
        icons = {
            'bicycle': '🚲',
            'bike': '🛵',
            'van': '🚐'
        }
        return f"{icons.get(self.vehicle_type, '')} {self.get_vehicle_type_display()}"