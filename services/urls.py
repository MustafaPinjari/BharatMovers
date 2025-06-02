from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('request-custom-service/', views.request_custom_service, name='request_custom_service'),
    path('delivery-partner-request/', views.delivery_partner_request, name='delivery_partner_request'),
    path('enterprise-request/', views.enterprise_request, name='enterprise_request'),
]