from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_info', 'service_info', 'pickup_date', 'status_badge', 'total_amount', 'created_at')
    list_filter = ('status', 'service', 'created_at', 'pickup_date')
    search_fields = ('customer__email', 'customer__username', 'pickup_location', 'delivery_location')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    ordering = ('-created_at',)
    actions = ['mark_as_confirmed', 'mark_as_in_progress', 'mark_as_completed', 'mark_as_cancelled']

    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'service')
        }),
        ('Booking Details', {
            'fields': ('pickup_location', 'delivery_location', 'pickup_date', 'total_distance', 'total_amount')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def booking_id(self, obj):
        return f'#{obj.id}'
    booking_id.short_description = 'Booking ID'

    def customer_info(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.customer.id])
        return format_html('<a href="{}">{} ({})</a>',
                         url,
                         obj.customer.get_full_name() or obj.customer.username,
                         obj.customer.email)
    customer_info.short_description = 'Customer'

    def service_info(self, obj):
        url = reverse('admin:services_service_change', args=[obj.service.id])
        return format_html('<a href="{}">{}</a>', url, obj.service.name)
    service_info.short_description = 'Service'

    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'CONFIRMED': 'blue',
            'IN_PROGRESS': 'purple',
            'COMPLETED': 'green',
            'CANCELLED': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED', updated_at=timezone.now())
    mark_as_confirmed.short_description = 'Mark selected bookings as Confirmed'

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='IN_PROGRESS', updated_at=timezone.now())
    mark_as_in_progress.short_description = 'Mark selected bookings as In Progress'

    def mark_as_completed(self, request, queryset):
        queryset.update(status='COMPLETED', updated_at=timezone.now())
    mark_as_completed.short_description = 'Mark selected bookings as Completed'

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED', updated_at=timezone.now())
    mark_as_cancelled.short_description = 'Mark selected bookings as Cancelled'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(customer=request.user)
