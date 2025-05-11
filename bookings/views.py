from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Booking
from services.models import Service

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'pickup_location', 'delivery_location', 'pickup_date', 'notes']
        widgets = {
            'pickup_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.status = 'PENDING'
            booking.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        form = BookingForm()
    return render(request, 'bookings/create_booking.html', {'form': form})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def update_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.status not in ['PENDING', 'CONFIRMED']:
        messages.error(request, 'Cannot update booking in current status.')
        return redirect('bookings:booking_detail', pk=booking.pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        form = BookingForm(instance=booking)
    return render(request, 'bookings/update_booking.html', {'form': form, 'booking': booking})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.status not in ['PENDING', 'CONFIRMED']:
        messages.error(request, 'Cannot cancel booking in current status.')
    else:
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
    return redirect('bookings:booking_detail', pk=booking.pk)
