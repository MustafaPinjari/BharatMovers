from django.contrib import admin
from django.utils.html import format_html
from .models import Service, VehicleType

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'price_per_km', 'display_image')
    search_fields = ('name', 'description')
    list_filter = ('capacity',)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;"/>',
                             obj.image.url)
        return '-'
    display_image.short_description = 'Vehicle Image'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'base_price', 'status_badge')
    list_filter = ('is_active', 'vehicle_type')
    search_fields = ('name', 'description')
    actions = ['activate_services', 'deactivate_services']

    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'description', 'base_price')
        }),
        ('Vehicle Details', {
            'fields': ('vehicle_type', 'is_active')
        }),
    )

    def status_badge(self, obj):
        if obj.is_active:
            color = 'green'
            status = 'Active'
        else:
            color = 'red'
            status = 'Inactive'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'

    def activate_services(self, request, queryset):
        queryset.update(is_active=True)
    activate_services.short_description = 'Activate selected services'

    def deactivate_services(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_services.short_description = 'Deactivate selected services'

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('base_price',)
        return []
