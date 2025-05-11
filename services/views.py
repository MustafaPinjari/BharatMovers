from django.shortcuts import render, get_object_or_404
from .models import Service, VehicleType

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
