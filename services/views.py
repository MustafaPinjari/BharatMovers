from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, VehicleType, CustomServiceRequest, DeliveryPartnerRequest, EnterpriseRequest
from accounts.models import UserMessage, CustomUser
from datetime import datetime
import logging

def service_list(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'services/service_list.html', {'services': services})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service})

def vehicle_list(request):
    vehicles = VehicleType.objects.all()
    return render(request, 'services/vehicle_list.html', {'vehicles': vehicles})

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(VehicleType, pk=pk)
    return render(request, 'services/vehicle_detail.html', {'vehicle': vehicle})

def service_page(request):
    """
    Main service page that displays the service booking form.
    """
    services = Service.objects.filter(is_active=True)
    return render(request, 'service.html', {'services': services})

@login_required
def request_custom_service(request):
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        description = request.POST.get('description')
        preferred_date = request.POST.get('preferred_date')
        
        if not all([service_type, description, preferred_date]):
            messages.error(request, "Please fill in all required fields")
            return redirect('accounts:profile')
        
        try:
            # Parse date string into date object
            parsed_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
            
            # Create the custom service request
            CustomServiceRequest.objects.create(
                user=request.user,
                service_type=service_type,
                description=description,
                preferred_date=parsed_date
            )
            
            messages.success(request, "Your custom service request has been submitted. Our team will review it shortly.")
            
            # Notify admin via message
            admin_users = CustomUser.objects.filter(is_staff=True)
            if admin_users.exists():
                admin = admin_users.first()
                UserMessage.objects.create(
                    user=admin,
                    sender=request.user,
                    subject=f"New Custom Service Request: {service_type}",
                    content=f"A new custom service request has been submitted by {request.user.get_full_name()}.\n\n"
                            f"Service Type: {service_type}\n"
                            f"Preferred Date: {preferred_date}\n\n"
                            f"Description: {description}",
                    is_read=False
                )
            
        except Exception as e:
            logging.debug(f"Error processing request: {str(e)}")
            logging.debug(f"Form data: {request.POST}")
            messages.error(request, f"Error processing your request: {str(e)}")
    
    return redirect('accounts:profile')

def delivery_partner_request(request):
    """
    Handle delivery partner registration form submission.
    Check if user is logged in before processing the form.
    """
    # Check if user is logged in
    if not request.user.is_authenticated:
        # Store the current page as next parameter for redirect back after login
        messages.info(request, "Please login first to submit your delivery partner application.")
        return redirect(f'/accounts/login/?next=/enterprises/')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        vehicle_type = request.POST.get('vehicle_type')
        
        # Validate form data
        if not all([first_name, last_name, email, phone_number, vehicle_type]):
            messages.error(request, "Please fill in all required fields")
            return redirect('dp')
        
        try:
            # Create the delivery partner request
            partner_request = DeliveryPartnerRequest.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                vehicle_type=vehicle_type,
                status='PENDING'
            )
            
            messages.success(request, "Your delivery partner application has been submitted successfully. Our team will review it shortly.")
            
            # Notify admin via message
            admin_users = CustomUser.objects.filter(is_staff=True)
            if admin_users.exists():
                admin = admin_users.first()
                UserMessage.objects.create(
                    user=admin,
                    sender=request.user,
                    subject=f"New Delivery Partner Request",
                    content=f"A new delivery partner request has been submitted by {request.user.get_full_name()}.\n\n"
                            f"Name: {first_name} {last_name}\n"
                            f"Email: {email}\n"
                            f"Phone: {phone_number}\n"
                            f"Vehicle Type: {vehicle_type}",
                    is_read=False
                )
            
        except Exception as e:
            logging.debug(f"Error processing request: {str(e)}")
            logging.debug(f"Form data: {request.POST}")
            messages.error(request, f"Error processing your request: {str(e)}")
    
    return redirect('dp')

def enterprise_request(request):
    """Handle enterprise requests from the enterprises.html form"""
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        
        print(f"DEBUG: Enterprise request received: {first_name} {last_name}, {email}, {phone}, {company}")
        
        # Create a new EnterpriseRequest object
        try:
            enterprise_request = EnterpriseRequest.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone,
                company_name=company
            )
            
            # Send notification to admin
            admin_users = CustomUser.objects.filter(is_staff=True)
            for admin in admin_users:
                UserMessage.objects.create(
                    user=admin,
                    sender=None,  # System message
                    subject="New Enterprise Request",
                    content=f"A new enterprise request has been submitted by {first_name} {last_name} from {company}.",
                    is_read=False
                )
            
            messages.success(request, "Your request has been submitted successfully. We'll get back to you soon!")
            return redirect('enterprises')
        
        except Exception as e:
            print(f"DEBUG: Error creating enterprise request: {str(e)}")
            messages.error(request, "There was a problem submitting your request. Please try again.")
    
    # If not POST or if there was an error, render the form again
    return render(request, 'enterprises.html')
