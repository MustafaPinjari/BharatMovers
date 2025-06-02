from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'department', 'designation', 'status_badge', 'join_date')
    list_filter = ('user_type', 'is_active', 'department')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('-join_date',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'username', 'password', 'phone_number', 'address')
        }),
        ('Role & Department', {
            'fields': ('user_type', 'department', 'designation')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type', 'phone_number')
        }),
    )

    def status_badge(self, obj):
        if obj.user_type == 'ADMIN':
            color = 'purple'
        elif obj.user_type == 'DRIVER':
            color = 'blue'
        else:
            color = 'green'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    
    status_badge.short_description = 'Status'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            if 'user_type' in form.base_fields:
                form.base_fields['user_type'].choices = [
                    choice for choice in form.base_fields['user_type'].choices
                    if choice[0] != 'ADMIN'
                ]
        return form
