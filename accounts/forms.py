from django import forms
from django.contrib.auth.forms import PasswordResetForm
from .models import CustomUser

class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        return CustomUser.objects.filter(email=email, is_active=True)