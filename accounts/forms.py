from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserChangeForm
from .models import CustomUser

class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        return CustomUser.objects.filter(email=email, is_active=True)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_image', 'email_notifications', 'sms_notifications']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'profile_image':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control-file'})