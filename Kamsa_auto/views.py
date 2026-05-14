from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicule, Reservation
from .forms import ReservationForm

# Create your views here.

def home(request):
    return render(request, 'index.html')



def reservation(request):
    return render(request, 'reservation.html')

def liste_vehicule(request):
    vehicules = Vehicule.objects.all()

    return render(request, 'vehicules.html', {
        'vehicules': vehicules
    })


@login_required
def reservation_vehicule(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.vehicule = vehicule

            # Vérification disponibilité
            overlapping = reservation.objects.filter(
                vehicule=vehicule,
                date_debut__lt=reservation.date_fin,
                date_fin__gt=reservation.date_debut
            )

            if overlapping.exists():
                form.add_error(None, "Ce véhicule est déjà réservé pour ces dates")
            else:
                reservation.save()
                return redirect('booking_success')

    else:
        form = ReservationForm()

    return render(request, 'reservation.html', {
        'form': form,
        'vehicle': vehicule
    })

def booking_success(request):
    return render(request, 'success.html')


def compte(request):
    return render(request, 'compte.html')


def contact(request):
    return render(request, 'contact.html')

