from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('dp/', TemplateView.as_view(template_name='dp.html'), name='dp'),
    path('services/', TemplateView.as_view(template_name='service.html'), name='service'),
    path('support/', TemplateView.as_view(template_name='support.html'), name='support'),
    path('career/', TemplateView.as_view(template_name='career.html'), name='career'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('refund/', TemplateView.as_view(template_name='refund.html'), name='refund'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('services/', include('services.urls')),
    path('bookings/', include('bookings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
