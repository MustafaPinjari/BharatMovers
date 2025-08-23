from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django import forms

from .models import CustomUser, EnterpriseRequest
from bookings.models import Booking
from services.models import Service, VehicleType

# Form Classes
class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['name', 'description', 'capacity', 'price_per_km', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        help_texts = {
            'price_per_km': 'Price per kilometer for this vehicle type',
            'capacity': 'Example: 1000kg, 3-4 rooms, etc.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Enter a detailed description of the vehicle type'})

# Admin Mixin
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

# User Management
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def users_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin/users.html', {
        'users': users,
        'active_tab': 'users'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'accounts/admin/user_detail.html', {
        'user_detail': user,
        'active_tab': 'users'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin/users.html', {
        'users': users,
        'active_tab': 'users'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'accounts/admin/view_user.html', {
        'user': user,
        'active_tab': 'users'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('accounts:admin_view_user', user_id=user.id)
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'accounts/admin/edit_user.html', {
        'form': form,
        'user': user,
        'active_tab': 'users'
    })

# Group Management
@login_required
@user_passes_test(lambda u: u.is_superuser)
def groups_list(request):
    groups = Group.objects.all()
    return render(request, 'accounts/admin/groups.html', {
        'groups': groups,
        'active_tab': 'groups'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_groups(request):
    groups = Group.objects.all()
    return render(request, 'accounts/admin/groups.html', {
        'groups': groups,
        'active_tab': 'groups'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_add_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                messages.success(request, f'Group "{name}" created successfully.')
            else:
                messages.info(request, f'Group "{name}" already exists.')
            return redirect('accounts:admin_groups')
    return render(request, 'accounts/admin/add_group.html', {
        'active_tab': 'groups'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_view_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'accounts/admin/view_group.html', {
        'group': group,
        'active_tab': 'groups'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_edit_group(request, group_id):
    """View to edit a group."""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group.name = name
            group.save()
            messages.success(request, 'Group updated successfully.')
            return redirect('accounts:admin_view_group', group_id=group.id)
    
    return render(request, 'accounts/admin/edit_group.html', {
        'group': group,
        'active_tab': 'groups'
    })

# Delivery Partners
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def delivery_partners(request):
    partners = CustomUser.objects.filter(user_type='DELIVERY_PARTNER').order_by('-date_joined')
    return render(request, 'accounts/admin/delivery_partners.html', {
        'partners': partners,
        'active_tab': 'delivery_partners'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_delivery_partners(request):
    """View to list all delivery partner requests."""
    from services.models import DeliveryPartnerRequest
    
    # Handle form submissions (approve/reject/delete)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        try:
            partner_request = DeliveryPartnerRequest.objects.get(id=request_id)
            
            if action == 'approve':
                partner_request.status = 'APPROVED'
                partner_request.save()
                # Optionally, you can set the user as a driver here
                user = partner_request.user
                user.is_driver = True
                user.save()
                messages.success(request, f"Successfully approved {partner_request.first_name}'s application.")
                
            elif action == 'reject':
                partner_request.status = 'REJECTED'
                partner_request.save()
                messages.success(request, f"Successfully rejected {partner_request.first_name}'s application.")
                
            elif action == 'delete':
                partner_request.delete()
                messages.success(request, "Request deleted successfully.")
                
        except DeliveryPartnerRequest.DoesNotExist:
            messages.error(request, "Request not found.")
    
    # Get all delivery partner requests, ordered by creation date (newest first)
    delivery_requests = DeliveryPartnerRequest.objects.all().order_by('-created_at')
    
    return render(request, 'accounts/admin/delivery_partners.html', {
        'delivery_requests': delivery_requests,
        'active_tab': 'delivery_partners'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_add_delivery_partner(request):
    if request.method == 'POST':
        form = DeliveryPartnerForm(request.POST)
        if form.is_valid():
            partner = form.save(commit=False)
            partner.is_delivery_partner = True
            partner.save()
            messages.success(request, 'Delivery partner added successfully.')
            return redirect('accounts:admin_delivery_partners')
    else:
        form = DeliveryPartnerForm()
    
    return render(request, 'accounts/admin/add_delivery_partner.html', {
        'form': form,
        'active_tab': 'delivery_partners'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_view_delivery_partner(request, partner_id):
    partner = get_object_or_404(CustomUser, id=partner_id, is_delivery_partner=True)
    return render(request, 'accounts/admin/view_delivery_partner.html', {
        'partner': partner,
        'active_tab': 'delivery_partners'
    })

# Enterprise Requests
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def enterprise_requests(request):
    requests = CustomUser.objects.filter(
        user_type='ENTERPRISE', 
        is_active=False
    ).order_by('-date_joined')
    return render(request, 'accounts/admin/enterprise_requests.html', {
        'requests': requests,
        'active_tab': 'enterprise_requests'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_enterprise_requests(request):
    """View to list all enterprise requests."""
    requests = EnterpriseRequest.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin/enterprise_requests.html', {
        'requests': requests,
        'active_tab': 'enterprise_requests'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_view_enterprise_request(request, request_id):
    req = get_object_or_404(EnterpriseRequest, id=request_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            req.status = status
            if status == 'approved':
                req.user.is_enterprise = True
                req.user.save()
            req.save()
            messages.success(request, f'Request {status} successfully.')
            return redirect('accounts:admin_enterprise_requests')
    
    return render(request, 'accounts/admin/view_enterprise_request.html', {
        'request': req,
        'active_tab': 'enterprise_requests'
    })

# Bookings
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_bookings(request):
    bookings = Booking.objects.select_related('customer', 'service').order_by('-created_at')
    return render(request, 'accounts/admin/bookings.html', {
        'bookings': bookings,
        'active_tab': 'bookings'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def view_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'accounts/admin/view_booking.html', {
        'booking': booking,
        'active_tab': 'bookings'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_view_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'accounts/admin/view_booking.html', {
        'booking': booking,
        'active_tab': 'bookings'
    })

# Services
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_services(request):
    services = Service.objects.all().order_by('name')
    return render(request, 'accounts/admin/services.html', {
        'services': services,
        'active_tab': 'services'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_view_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'accounts/admin/view_service.html', {
        'service': service,
        'active_tab': 'services'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('accounts:admin_view_service', service_id=service.id)
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'accounts/admin/edit_service.html', {
        'form': form,
        'service': service,
        'active_tab': 'services'
    })

# Vehicle Types
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_vehicle_types(request):
    """View to list all vehicle types."""
    vehicle_types = VehicleType.objects.all().order_by('name').order_by('name').order_by('name')
    return render(request, 'accounts/admin/vehicle_types.html', {
        'vehicle_types': vehicle_types,
        'active_tab': 'vehicle_types'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_add_vehicle_type(request):
    """View to add a new vehicle type."""
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle type added successfully.')
            return redirect('accounts:admin_vehicle_types')
    else:
        form = VehicleTypeForm()
    
    return render(request, 'accounts/admin/add_vehicle_type.html', {
        'form': form,
        'active_tab': 'vehicle_types'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_add_vehicle_type(request):
    """View to add a new vehicle type."""
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle type added successfully.')
            return redirect('accounts:admin_vehicle_types')
    else:
        form = VehicleTypeForm()
    
    return render(request, 'accounts/admin/add_vehicle_type.html', {
        'form': form,
        'active_tab': 'vehicle_types'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_add_vehicle_type(request):
    """View to add a new vehicle type."""
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle type added successfully.')
            return redirect('accounts:admin_vehicle_types')
    else:
        form = VehicleTypeForm()
    
    return render(request, 'accounts/admin/add_vehicle_type.html', {
        'form': form,
        'active_tab': 'vehicle_types'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_view_vehicle_type(request, vehicle_type_id):
    """View to see details of a specific vehicle type."""
    vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)
    return render(request, 'accounts/admin/view_vehicle_type.html', {
        'vehicle_type': vehicle_type,
        'active_tab': 'vehicle_types'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_edit_vehicle_type(request, vehicle_type_id):
    """View to edit a vehicle type."""
    vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)
    
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST, request.FILES, instance=vehicle_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle type updated successfully.')
            return redirect('accounts:admin_view_vehicle_type', vehicle_type_id=vehicle_type.id)
    else:
        form = VehicleTypeForm(instance=vehicle_type)
    
    return render(request, 'accounts/admin/edit_vehicle_type.html', {
        'form': form,
        'vehicle_type': vehicle_type,
        'active_tab': 'vehicle_types'
    })

def register(request):
    if request.method == 'POST':
        # Get form data
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        
        # Validate required fields
        if not all([fullname, email, phone, password, confirm_password]):
            messages.error(request, 'All fields are required')
            return render(request, 'accounts/register.html')
        
        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address')
            return render(request, 'accounts/register.html')
        
        # Validate phone number (10 digits)
        import re
        if not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Please enter a valid 10-digit phone number')
            return render(request, 'accounts/register.html')
        
        # Validate password
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'accounts/register.html')
        
        if not any(char.isupper() for char in password):
            messages.error(request, 'Password must contain at least one uppercase letter')
            return render(request, 'accounts/register.html')
            
        if not any(char.isdigit() for char in password):
            messages.error(request, 'Password must contain at least one number')
            return render(request, 'accounts/register.html')
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html')
        
        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'accounts/register.html')
        
        try:
            # Split fullname into first_name and last_name
            name_parts = fullname.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Create user
            user = CustomUser.objects.create_user(
                username=email,  # Using email as username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone
            )
            
            messages.success(request, 'Registration successful! Please login to continue.')
            return redirect('accounts:login')
            
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember') == 'on'
        
        if not email or not password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'accounts/login.html')
        
        # Authenticate using email as username since USERNAME_FIELD = 'email'
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                
                # Handle remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Session expires when browser closes
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                
                # Redirect based on user type
                next_url = request.GET.get('next')
                
                if next_url:
                    return redirect(next_url)
                elif user.is_superuser or user.is_staff or getattr(user, 'user_type', '').lower() == 'admin':
                    return redirect('accounts:admin_dashboard')  # Redirect to custom admin dashboard
                else:
                    return redirect('accounts:profile')  # Regular user dashboard
            else:
                messages.error(request, 'Your account is inactive. Please contact support.')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def profile(request):
    context = {
        'user': request.user,
        'bookings': request.user.bookings.all().order_by('-created_at')[:5]  # Get last 5 bookings
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get form data
        fullname = request.POST.get('fullname', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        # Update name if provided
        if fullname:
            name_parts = fullname.split(maxsplit=1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Update phone if provided and valid
        if phone:
            import re
            if not re.match(r'^\d{10}$', phone):
                messages.error(request, 'Please enter a valid 10-digit phone number')
                return redirect('accounts:edit_profile')
            user.phone_number = phone
        
        # Update address if provided
        if address:
            user.address = address
        
        # Handle password change if requested
        if current_password and new_password and confirm_password:
            # Verify current password
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
                return redirect('accounts:edit_profile')
            
            # Validate new password
            if len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters long')
                return redirect('accounts:edit_profile')
            
            if not any(char.isupper() for char in new_password):
                messages.error(request, 'New password must contain at least one uppercase letter')
                return redirect('accounts:edit_profile')
                
            if not any(char.isdigit() for char in new_password):
                messages.error(request, 'New password must contain at least one number')
                return redirect('accounts:edit_profile')
            
            # Check if new passwords match
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return redirect('accounts:edit_profile')
            
            # Set new password
            user.set_password(new_password)
            messages.success(request, 'Password updated successfully!')
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            
            # If password was changed, user needs to login again
            if current_password and new_password and confirm_password:
                return redirect('accounts:login')
                
            return redirect('accounts:profile')
            
        except Exception as e:
            messages.error(request, 'An error occurred while updating your profile. Please try again.')
            return redirect('accounts:edit_profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required
def send_message(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if subject and message:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                # Send email to admin
                admin_email = settings.DEFAULT_FROM_EMAIL  # Make sure this is set in your settings.py
                user_email = request.user.email
                full_message = f"""
                New message from {request.user.get_full_name()} ({user_email}):
                
                Subject: {subject}
                
                {message}
                """
                
                send_mail(
                    subject=f"[BharatMovers] {subject}",
                    message=full_message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('accounts:profile')
                
            except Exception as e:
                messages.error(request, 'Failed to send message. Please try again later.')
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send message: {str(e)}")
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return redirect('accounts:profile')

@login_required
def update_preferences(request):
    if request.method == 'POST':
        try:
            user = request.user
            # Update email notifications preference
            user.email_notifications = 'email_notifications' in request.POST
            # Update SMS notifications preference
            user.sms_notifications = 'sms_notifications' in request.POST
            user.save()
            messages.success(request, 'Your preferences have been updated successfully!')
        except Exception as e:
            messages.error(request, 'Failed to update preferences. Please try again.')
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update preferences: {str(e)}")
    
    return redirect('accounts:profile')

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    from bookings.models import Booking
    from services.models import Service, VehicleType
    
    # Get all the data needed for the dashboard
    total_users = CustomUser.objects.count()
    total_bookings = Booking.objects.count()
    total_services = Service.objects.count()
    total_vehicle_types = VehicleType.objects.count()
    
    # Recent bookings (last 5)
    recent_bookings = Booking.objects.select_related('customer', 'service').order_by('-created_at')[:5]
    
    context = {
        'active_tab': 'dashboard',  # This highlights the dashboard tab in the sidebar
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_services': total_services,
        'total_vehicle_types': total_vehicle_types,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'accounts/admin/dashboard.html', context)

@login_required
def admin_add_user(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:admin_dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('accounts:admin_users')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/admin/add_user.html', {
        'form': form,
        'active_tab': 'users',
    })

@login_required
def admin_add_service(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:admin_dashboard')
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, 'Service added successfully.')
            return redirect('accounts:admin_services')
    else:
        form = ServiceForm()
    
    return render(request, 'accounts/admin/add_service.html', {
        'form': form,
        'active_tab': 'services',
    })

@login_required
def admin_add_vehicle_type(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:admin_dashboard')
    
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle_type = form.save()
            messages.success(request, 'Vehicle type added successfully.')
            return redirect('accounts:admin_vehicle_types')
    else:
        form = VehicleTypeForm()
    
    return render(request, 'accounts/admin/add_vehicle_type.html', {
        'form': form,
        'active_tab': 'vehicle_types',
    })
