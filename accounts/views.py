from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import CustomUser

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
                login(request, user)
                
                # Handle remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Session expires when browser closes
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                
                # Redirect to next URL if specified, otherwise home
                next_url = request.GET.get('next', 'home')
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
    context = {
        'user': request.user,
        'bookings': request.user.booking_set.all().order_by('-created_at')[:5]  # Get last 5 bookings
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
            if current_password and new_password and confirm_password:
                return redirect('accounts:login')
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        except Exception as e:
            messages.error(request, 'An error occurred while updating your profile. Please try again.')
            return redirect('accounts:edit_profile')
    
    form = UserRegistrationForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
