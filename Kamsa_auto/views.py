from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Client, Vehicule, Reservation 
from .forms import ReservationForm
from .forms import InscriptionForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfilForm

# Create your views here.
def home(request):
    return render(request, 'index.html')
    if request.user.is_authenticated:
        print("Utilisateur connecté")
    else:
        print("Utilisateur non connecté")

def reservation(request):
    return render(request, 'reservation.html')

def liste_vehicule(request):
    vehicules = Vehicule.objects.all()

    return render(request, 'vehicules.html', {
        'vehicules': vehicules
    })

def booking_success(request):
    return render(request, 'success.html')

def connexion(request):
    return render(request, 'connexion.html')

def contact(request):
    return render(request, 'contact.html')

# Inscription, Connexion & Deconnexion.
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)

        if form.is_valid():
            user = form.save()

            Client.objects.create(
                user=user,
                telephone=""
            )

            return redirect('connexion')
    else:
        form = InscriptionForm()

    return render(request, 'inscription.html', {'form': form})


def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(
                request,
                'connexion.html',
                {'erreur': 'Nom d’utilisateur ou mot de passe incorrect'}
            )

    return render(request, 'connexion.html')




def deconnexion(request):
    logout(request)
    return redirect('connexion')

@login_required
def reservation_vehicule(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.vehicule = vehicule
            # --- CALCUL DU PRIX TOTAL CÔTÉ SERVEUR ---
            # 1. Récupérer le nombre de jours
            delta_jours = (reservation.date_fin - reservation.date_debut).days
            if delta_jours <= 0:
                delta_jours = 1 # Sécurité au cas où c'est la même journée
                
            # 2. Calcul de base (Prix du véhicule x Jours)
            total = vehicule.prix_par_jour * delta_jours
            
            # 3. Ajouter l'option chauffeur si cochée
            avec_chauffeur = "chauffeur" in request.POST
            reservation.inclut_chauffeur = avec_chauffeur
            if avec_chauffeur:
                total += 10000  # Option forfaitaire ou (10000 * delta_jours) selon votre choix
                
            # Enregistrer le total calculé dans le modèle
            reservation.prix_total = total
            # -----------------------------------------
            
            overlapping = Reservation.objects.filter(
                vehicule=vehicule,
                date_debut__lt=reservation.date_fin,
                date_fin__gt=reservation.date_debut
            )

            if overlapping.exists():
                form.add_error(None, "Ce véhicule est déjà réservé pour ces dates.")
            else:
                reservation.save()
                return redirect('booking_success') # Assurez-vous que cette URL existe
        else:
            # Si le formulaire n'est pas valide, on peut voir les erreurs dans le terminal
            print(form.errors)
            
    else:
        form = ReservationForm()

    return render(request, 'reservation.html', {
        'form': form,
        'vehicule': vehicule
    })

@login_required
def dashboard(request):
    reservations = Reservation.objects.filter(user=request.user)
    

    return render(
        request,
        'dashboard.html',
        {
            'reservations': reservations
        }
    )



@login_required
def modifier_profil(request):

    if request.method == 'POST':
        form = ProfilForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()

            request.user.client.telephone = form.cleaned_data['telephone']
            request.user.client.save()

            return redirect('dashboard')

    else:
        form = ProfilForm(instance=request.user)

        form.fields['telephone'].initial = (
            request.user.client.telephone
        )

    return render(
        request,
        'modifier_profil.html',
        {'form': form}
    )



