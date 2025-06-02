from django.db import models

class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.CharField(max_length=50)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CustomServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='service_requests')
    service_type = models.CharField(max_length=100)
    description = models.TextField()
    preferred_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.service_type} - {self.user.email} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']

class DeliveryPartnerRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='delivery_partner_requests')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.vehicle_type} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']

class EnterpriseRequest(models.Model):
    """Model to store enterprise client requests"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    company_name = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('PENDING', 'Pending'),
            ('CONTACTED', 'Contacted'),
            ('CLOSED', 'Closed')
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['-created_at']
