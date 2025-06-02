from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/send-message/', views.send_message, name='send_message'),
    path('profile/update-preferences/', views.update_preferences, name='update_preferences'),
    
    # Custom Admin URLs
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/add/', views.admin_add_user, name='admin_add_user'),
    path('admin/users/<int:user_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/groups/', views.admin_groups, name='admin_groups'),
    path('admin/groups/add/', views.admin_add_group, name='admin_add_group'),
    path('admin/groups/<int:group_id>/edit/', views.admin_edit_group, name='admin_edit_group'),
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/bookings/<int:booking_id>/', views.admin_view_booking, name='admin_view_booking'),
    path('admin/services/', views.admin_services, name='admin_services'),
    path('admin/services/add/', views.admin_add_service, name='admin_add_service'),
    path('admin/services/<int:service_id>/edit/', views.admin_edit_service, name='admin_edit_service'),
    path('admin/vehicle-types/', views.admin_vehicle_types, name='admin_vehicle_types'),
    path('admin/vehicle-types/add/', views.admin_add_vehicle_type, name='admin_add_vehicle_type'),
    path('admin/vehicle-types/<int:vehicle_type_id>/edit/', views.admin_edit_vehicle_type, name='admin_edit_vehicle_type'),
    path('admin/delivery-partners/', views.admin_delivery_partners, name='admin_delivery_partners'),
    path('admin/enterprise-requests/', views.admin_enterprise_requests, name='admin_enterprise_requests'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]