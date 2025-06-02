from django.shortcuts import render
from services.models import Service, VehicleType
from django.db.models import Q

def home(request):
    query = request.GET.get('q', '')
    services = []
    vehicles = []
    
    if query:
        services = Service.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).filter(is_active=True)[:4]
        
        vehicles = VehicleType.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:6]
    else:
        # Display featured services and vehicles by default
        services = Service.objects.filter(is_active=True)[:4]
        vehicles = VehicleType.objects.all()[:6]
    
    context = {
        'services': services,
        'vehicles': vehicles,
        'search_query': query
    }
    return render(request, 'home.html', context)

def faqs_view(request):
    return render(request, 'faqs.html')