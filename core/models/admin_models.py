import uuid
from django.db import models

class FraudFlag(models.Model):
    DECISION_CHOICES = [
        ('pending', 'Pending Review'),
        ('vendor_correct', 'Vendor Correct'),
        ('vendor_fraud', 'Vendor Fraud'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(
        'Product', 
        on_delete=models.CASCADE,
        related_name='fraud_flag'
    )
    
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    variance_details = models.JSONField(default=dict)
    
    admin_reviewed = models.BooleanField(default=False)
    admin_decision = models.CharField(
        max_length=20, 
        choices=DECISION_CHOICES, 
        default='pending'
    )
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'fraud_flags'
        verbose_name = 'Fraud Flag'
        verbose_name_plural = 'Fraud Flags'
    
    def __str__(self):
        return f"Flag #{self.id} - Risk: {self.risk_score}"