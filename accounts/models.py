from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
        ('DRIVER', 'Driver')
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='CUSTOMER')
    is_customer = models.BooleanField(default=True)
    is_driver = models.BooleanField(default=False)
    department = models.CharField(max_length=50, blank=True)
    designation = models.CharField(max_length=50, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def is_admin_user(self):
        return self.user_type == 'ADMIN'

    def save(self, *args, **kwargs):
        if self.user_type == 'ADMIN':
            self.is_staff = True
            self.is_customer = False
            self.is_driver = False
        elif self.user_type == 'DRIVER':
            self.is_driver = True
            self.is_customer = False
        else:
            self.is_customer = True
            self.is_driver = False
        super().save(*args, **kwargs)


class UserMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    reply = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.user.email}"

    class Meta:
        ordering = ['-created_at']
