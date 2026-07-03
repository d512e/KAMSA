import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Client, Vehicule, Reservation 
from .forms import ReservationForm, InscriptionForm, ProfilForm

# --- VUES GÉNÉRALES ---
def home(request):
    if request.user.is_authenticated:
        print("Utilisateur connecté")
    else:
        print("Utilisateur non connecté")
    return render(request, 'index.html')

def reservation(request):
    return render(request, 'reservation.html')

def liste_vehicule(request):
    vehicules = Vehicule.objects.all()
    return render(request, 'vehicules.html', {'vehicules': vehicules})

def booking_success(request):
    return render(request, 'success.html')

def contact(request):
    return render(request, 'contact.html')


# --- AUTHENTIFICATION ---
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(user=user, telephone="")
            return redirect('connexion')
    else:
        form = InscriptionForm()
    return render(request, 'inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'connexion.html', {'erreur': 'Nom d’utilisateur ou mot de passe incorrect'})
    return render(request, 'connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion')


# --- CLIENT & RESERVATION ---
@login_required
def reservation_vehicule(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, id=vehicule_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.vehicule = vehicule
            
            # Calcul du prix côté serveur
            delta_jours = (reservation.date_fin - reservation.date_debut).days
            if delta_jours <= 0:
                delta_jours = 1
                
            total = vehicule.prix_par_jour * delta_jours
            
            avec_chauffeur = "chauffeur" in request.POST
            reservation.inclut_chauffeur = avec_chauffeur
            if avec_chauffeur:
                total += 10000 
                
            reservation.prix_total = total
            
            # Vérification des doublons de dates
            overlapping = Reservation.objects.filter(
                vehicule=vehicule,
                date_debut__lt=reservation.date_fin,
                date_fin__gt=reservation.date_debut
            )

            if overlapping.exists():
                form.add_error(None, "Ce véhicule est déjà réservé pour ces dates.")
            else:
                reservation.save()
                return redirect('page_paiement', reservation_id=reservation.id)
        else:
            print(form.errors)
    else:
        form = ReservationForm()

    return render(request, 'reservation.html', {'form': form, 'vehicule': vehicule})

@login_required
def dashboard(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'reservations': reservations})

@login_required
def modifier_profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.client.telephone = form.cleaned_data['telephone']
            request.user.client.save()
            return redirect('dashboard')
    else:
        form = ProfilForm(instance=request.user)
        form.fields['telephone'].initial = request.user.client.telephone

    return render(request, 'modifier_profil.html', {'form': form})

@login_required
def profil_utilisateur(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profil.html', {'reservations': reservations})


# --- ÉTAPES DU PAIEMENT SIMULÉ ---
@login_required
def page_paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, "paiement.html", {"reservation": reservation})

@login_required
def initier_paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        moyen = request.POST.get("moyen_paiement", "Inconnu")

        # 1. Vérification selon le choix
        if moyen == "carte":
            nom_titulaire = request.POST.get("nom_carte", "").strip()
            num_carte = request.POST.get("numero_carte", "").strip()
            
            if not nom_titulaire or not num_carte:
                messages.error(request, "Veuillez remplir les informations de votre carte bancaire.")
                return redirect("page_paiement", reservation_id=reservation.id)
                
            info_log = f"Carte de {nom_titulaire}"
        else:
            telephone = request.POST.get("telephone_paiement", "").strip()
            if not telephone:
                messages.error(request, "Veuillez saisir votre numéro Mobile Money.")
                return redirect("page_paiement", reservation_id=reservation.id)
                
            info_log = f"Compte {telephone}"

        # 2. Processus de validation de la transaction simulée
        transaction = "PIZ-" + uuid.uuid4().hex[:12].upper()

        reservation.transaction_id = transaction
        reservation.statut_paiement = "paid"
        reservation.status = "confirmed"
        reservation.save()

        # Message de notification dynamique
        nom_moyen = "Carte Bancaire" if moyen == "carte" else moyen.upper()
        messages.success(
            request, 
            f"Paiement de {reservation.prix_total} FCFA validé via {nom_moyen} ({info_log})."
        )
        
        return redirect("paiement_succes", reservation_id=reservation.id)

    return redirect("page_paiement", reservation_id=reservation.id)

@login_required
def paiement_succes(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, "paiement_succes.html", {"reservation": reservation})