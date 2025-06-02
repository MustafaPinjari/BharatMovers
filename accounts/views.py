from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django import forms
from .models import CustomUser
from bookings.models import Booking
from services.models import Service, VehicleType, CustomServiceRequest, DeliveryPartnerRequest, EnterpriseRequest
from django.views.decorators.csrf import csrf_protect

def register(request):
    if request.method == 'POST':
        # Get form data
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
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
                phone_number=phone,
                address=address
            )
            
            messages.success(request, 'Registration successful! Please login to continue.')
            return redirect('accounts:login')
            
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')

@csrf_protect
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
                login(request, user)
                
                # Handle remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Session expires when browser closes
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                
                # Role-based redirection
                if user.is_superuser or user.is_staff:
                    return redirect('accounts:admin_dashboard')  # Redirect to our custom admin dashboard
                else:
                    # Redirect to next URL if specified, otherwise profile
                    next_url = request.GET.get('next', 'accounts:profile')
                    return redirect(next_url)
            else:
                messages.error(request, 'Your account is inactive. Please contact support.')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def profile(request):
    # Get user's bookings with counts for different statuses
    user_bookings = request.user.bookings.all().order_by('-created_at')
    recent_bookings = user_bookings[:5]  # Get last 5 bookings
    
    # Count bookings by status
    completed_count = user_bookings.filter(status='COMPLETED').count()
    pending_count = user_bookings.filter(status='PENDING').count()
    
    # Get all services for the services tab
    services = Service.objects.all()
    
    # Get user messages
    from .models import UserMessage
    messages_list = UserMessage.objects.filter(user=request.user).order_by('-created_at')
    unread_messages_count = messages_list.filter(is_read=False, sender__isnull=True).count()
    
    # Get custom service requests
    service_requests = CustomServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'bookings': recent_bookings,
        'all_bookings': user_bookings,
        'bookings_count': user_bookings.count(),
        'completed_count': completed_count,
        'pending_count': pending_count,
        'services': services,
        'service_requests': service_requests,
        'messages_list': messages_list,
        'unread_messages_count': unread_messages_count,
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
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')
        
        if subject and message_content:
            # Create a new message from user to admin
            from .models import UserMessage
            admin_users = CustomUser.objects.filter(is_staff=True)
            if admin_users.exists():
                admin = admin_users.first()
                UserMessage.objects.create(
                    user=admin,  # Message is for admin
                    sender=request.user,  # User is the sender
                    subject=subject,
                    content=message_content,
                    is_read=False  # Not read by admin yet
                )
                messages.success(request, "Your message has been sent to the admin team.")
            else:
                messages.error(request, "Could not find admin user to send message to.")
        else:
            messages.error(request, "Please provide both subject and message.")
    
    return redirect('accounts:profile')

@login_required
def update_preferences(request):
    if request.method == 'POST':
        email_notifications = request.POST.get('email_notifications') == 'on'
        sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        # Update user preferences - if these fields don't exist, we'll add them as custom attributes
        user = request.user
        user.email_notifications = email_notifications
        user.sms_notifications = sms_notifications
        user.save()
        
        messages.success(request, "Your preferences have been updated.")
    
    return redirect('accounts:profile')

# Admin access check function
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

# Custom Admin Panel views
@user_passes_test(is_admin)
def admin_dashboard(request):
    # User stats
    total_users = CustomUser.objects.count()
    
    # Booking stats
    total_bookings = Booking.objects.count()
    recent_bookings = Booking.objects.order_by('-created_at')[:5]
    
    # Status counts
    pending_count = Booking.objects.filter(status='PENDING').count()
    confirmed_count = Booking.objects.filter(status='CONFIRMED').count()
    in_progress_count = Booking.objects.filter(status='IN_PROGRESS').count()
    completed_count = Booking.objects.filter(status='COMPLETED').count()
    cancelled_count = Booking.objects.filter(status='CANCELLED').count()
    
    # Service stats
    total_services = Service.objects.count()
    
    # Vehicle type stats
    total_vehicle_types = VehicleType.objects.count()
    
    context = {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_services': total_services,
        'total_vehicle_types': total_vehicle_types,
        'recent_bookings': recent_bookings,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'active_tab': 'dashboard'
    }
    return render(request, 'accounts/admin/dashboard.html', context)

@user_passes_test(is_admin)
def admin_users(request):
    users = CustomUser.objects.all().order_by('first_name', 'last_name')
    
    context = {
        'users': users,
        'active_tab': 'users'
    }
    return render(request, 'accounts/admin/users.html', context)

@user_passes_test(is_admin)
def admin_add_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        is_staff = request.POST.get('is_staff') == 'on'
        password = request.POST.get('password')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('accounts:admin_add_user')
        
        try:
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                address=address,
                is_staff=is_staff
            )
            messages.success(request, f'User {email} created successfully')
            return redirect('accounts:admin_users')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'accounts/admin/add_user.html', {'active_tab': 'users'})

@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone')
        user.address = request.POST.get('address', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Only update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, f'User {user.email} updated successfully')
        return redirect('accounts:admin_users')
    
    return render(request, 'accounts/admin/edit_user.html', {'user': user, 'active_tab': 'users'})

@user_passes_test(is_admin)
def admin_groups(request):
    groups = Group.objects.all()
    
    context = {
        'groups': groups,
        'active_tab': 'groups'
    }
    return render(request, 'accounts/admin/groups.html', context)

@user_passes_test(is_admin)
def admin_add_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if Group.objects.filter(name=name).exists():
            messages.error(request, 'Group already exists')
            return redirect('accounts:admin_add_group')
        
        try:
            group = Group.objects.create(name=name)
            messages.success(request, f'Group {name} created successfully')
            return redirect('accounts:admin_groups')
        except Exception as e:
            messages.error(request, f'Error creating group: {str(e)}')
    
    return render(request, 'accounts/admin/add_group.html', {'active_tab': 'groups'})

@user_passes_test(is_admin)
def admin_edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        group.name = request.POST.get('name')
        group.save()
        messages.success(request, f'Group {group.name} updated successfully')
        return redirect('accounts:admin_groups')
    
    return render(request, 'accounts/admin/edit_group.html', {'group': group, 'active_tab': 'groups'})

@user_passes_test(is_admin)
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'active_tab': 'bookings'
    }
    return render(request, 'accounts/admin/bookings.html', context)

@user_passes_test(is_admin)
def admin_view_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        total_amount = request.POST.get('total_amount')
        
        if status:
            booking.status = status
            
        # Update total_amount if provided, regardless of status
        if total_amount:
            try:
                booking.total_amount = float(total_amount)
            except (ValueError, TypeError):
                messages.warning(request, f'Invalid amount format. Booking status updated but amount not changed.')
        
        booking.save()
        messages.success(request, f'Booking #{booking.id} updated successfully')
        return redirect('accounts:admin_bookings')
    
    return render(request, 'accounts/admin/view_booking.html', {'booking': booking, 'active_tab': 'bookings'})

@user_passes_test(is_admin)
def admin_services(request):
    services = Service.objects.all().order_by('name')
    
    context = {
        'services': services,
        'active_tab': 'services'
    }
    return render(request, 'accounts/admin/services.html', context)

@user_passes_test(is_admin)
def admin_add_service(request):
    vehicle_types = VehicleType.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        base_price = request.POST.get('base_price')
        vehicle_type_id = request.POST.get('vehicle_type')
        
        try:
            vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
            service = Service.objects.create(
                name=name,
                description=description,
                base_price=base_price,
                vehicle_type=vehicle_type,
                is_active=True
            )
            messages.success(request, f'Service {name} created successfully')
            return redirect('accounts:admin_services')
        except Exception as e:
            messages.error(request, f'Error creating service: {str(e)}')
    
    return render(request, 'accounts/admin/add_service.html', {'active_tab': 'services', 'vehicle_types': vehicle_types})

@user_passes_test(is_admin)
def admin_edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.base_price = request.POST.get('base_price')
        service.vehicle_type_id = request.POST.get('vehicle_type')
        service.is_active = request.POST.get('is_active') == 'on'
        service.save()
        messages.success(request, f'Service {service.name} updated successfully')
        return redirect('accounts:admin_services')
    
    return render(request, 'accounts/admin/edit_service.html', {'service': service, 'active_tab': 'services'})

@user_passes_test(is_admin)
def admin_vehicle_types(request):
    vehicle_types = VehicleType.objects.all().order_by('name')
    
    context = {
        'vehicle_types': vehicle_types,
        'active_tab': 'vehicle_types'
    }
    return render(request, 'accounts/admin/vehicle_types.html', context)

@user_passes_test(is_admin)
def admin_add_vehicle_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        capacity = request.POST.get('capacity')
        price_per_km = request.POST.get('price_per_km')
        
        try:
            vehicle_type = VehicleType.objects.create(
                name=name,
                description=description,
                capacity=capacity,
                price_per_km=price_per_km
            )
            messages.success(request, f'Vehicle type {name} created successfully')
            return redirect('accounts:admin_vehicle_types')
        except Exception as e:
            messages.error(request, f'Error creating vehicle type: {str(e)}')
    
    return render(request, 'accounts/admin/add_vehicle_type.html', {'active_tab': 'vehicle_types'})

@user_passes_test(is_admin)
def admin_edit_vehicle_type(request, vehicle_type_id):
    vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)
    
    if request.method == 'POST':
        vehicle_type.name = request.POST.get('name')
        vehicle_type.description = request.POST.get('description')
        vehicle_type.capacity = request.POST.get('capacity')
        vehicle_type.price_per_km = request.POST.get('price_per_km')
        vehicle_type.is_active = request.POST.get('is_active') == 'on'
        vehicle_type.save()
        messages.success(request, f'Vehicle type {vehicle_type.name} updated successfully')
        return redirect('accounts:admin_vehicle_types')
    
    return render(request, 'accounts/admin/edit_vehicle_type.html', {'vehicle_type': vehicle_type, 'active_tab': 'vehicle_types'})

@user_passes_test(is_admin)
def admin_delivery_partners(request):
    from services.models import DeliveryPartnerRequest
    
    # Handle actions (approve, reject, delete)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        print(f"DEBUG: Received POST with request_id={request_id}, action={action}")
        print(f"DEBUG: POST data: {request.POST}")
        
        try:
            partner_request = DeliveryPartnerRequest.objects.get(id=request_id)
            print(f"DEBUG: Found partner request: {partner_request}")
            
            if action == 'approve':
                partner_request.status = 'APPROVED'
                partner_request.save()
                # Notify the user that their request was approved
                from .models import UserMessage
                UserMessage.objects.create(
                    user=partner_request.user,
                    sender=request.user,
                    subject="Delivery Partner Application Approved",
                    content=f"Congratulations! Your application to become a delivery partner has been approved.",
                    is_read=False
                )
                messages.success(request, f"Delivery partner request from {partner_request.first_name} {partner_request.last_name} has been approved.")
                print(f"DEBUG: Approved request, set messages")
            
            elif action == 'reject':
                partner_request.status = 'REJECTED'
                partner_request.save()
                # Notify the user that their request was rejected
                from .models import UserMessage
                UserMessage.objects.create(
                    user=partner_request.user,
                    sender=request.user,
                    subject="Delivery Partner Application Status",
                    content=f"We regret to inform you that your application to become a delivery partner has been rejected.",
                    is_read=False
                )
                messages.success(request, f"Delivery partner request from {partner_request.first_name} {partner_request.last_name} has been rejected.")
                print(f"DEBUG: Rejected request, set messages")
            
            elif action == 'delete':
                partner_name = f"{partner_request.first_name} {partner_request.last_name}"
                partner_request.delete()
                messages.success(request, f"Delivery partner request from {partner_name} has been deleted.")
                print(f"DEBUG: Deleted request, set messages")
            
            # Redirect to the same page to avoid form resubmission
            return redirect('accounts:admin_delivery_partners')
                
        except DeliveryPartnerRequest.DoesNotExist:
            messages.error(request, "Request not found.")
            print(f"DEBUG: Request not found error")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            print(f"DEBUG: Exception: {str(e)}")
    
    delivery_requests = DeliveryPartnerRequest.objects.all().order_by('-created_at')
    
    context = {
        'delivery_requests': delivery_requests,
        'active_tab': 'delivery_partners'
    }
    return render(request, 'accounts/admin/delivery_partners.html', context)

@user_passes_test(is_admin)
def admin_enterprise_requests(request):
    """View for admins to manage enterprise requests"""
    from services.models import EnterpriseRequest
    
    # Handle actions (mark as contacted, delete)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        print(f"DEBUG: Enterprise admin received POST with request_id={request_id}, action={action}")
        
        try:
            enterprise_request = EnterpriseRequest.objects.get(id=request_id)
            
            if action == 'contacted':
                enterprise_request.status = 'CONTACTED'
                enterprise_request.save()
                messages.success(request, f"Enterprise request from {enterprise_request.company_name} marked as contacted.")
            
            elif action == 'close':
                enterprise_request.status = 'CLOSED'
                enterprise_request.save()
                messages.success(request, f"Enterprise request from {enterprise_request.company_name} marked as closed.")
            
            elif action == 'delete':
                company_name = enterprise_request.company_name
                enterprise_request.delete()
                messages.success(request, f"Enterprise request from {company_name} has been deleted.")
            
            # Redirect to avoid form resubmission
            return redirect('accounts:admin_enterprise_requests')
                
        except EnterpriseRequest.DoesNotExist:
            messages.error(request, "Request not found.")
            print(f"DEBUG: Enterprise request not found error")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            print(f"DEBUG: Exception: {str(e)}")
    
    enterprise_requests = EnterpriseRequest.objects.all().order_by('-created_at')
    
    context = {
        'enterprise_requests': enterprise_requests,
        'active_tab': 'enterprise_requests'
    }
    return render(request, 'accounts/admin/enterprise_requests.html', context)
