import uuid
import datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Client, Vehicule, Reservation 
from .forms import ReservationForm, InscriptionForm, ProfilForm
from decimal import Decimal  # <-- ÉTAPE 1 : AJOUTER CET IMPORT TOUT EN HAUT

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

def apropos(request):
    return render(request, 'apropos.html')

def termes_conditions(request):
    return render(request, 'termes_et_conditions.html')

def politique_confidentialite(request):
    return render(request, 'politiques_et_confidentialite.html')


# --- AUTHENTIFICATION ---
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Sauvegarde de l'utilisateur (User standard)
            user = form.save()
            
            # 2. Récupération des champs personnalisés
            telephone = form.cleaned_data.get('telephone')
            permis = form.cleaned_data.get('permis_conduire')
            
            # 3. Création du profil Client associé
            Client.objects.create(
                user=user,
                telephone=telephone,
                permis_conduire=permis
            )
            
            messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
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
            
            # Récupération des options choisies dans le formulaire HTML
            est_abonnement = "abonnement_mensuel" in request.POST
            avec_chauffeur = "chauffeur" in request.POST
            
            # --- CALCUL DU PRIX ET DURÉE SELON LE MODE ---
            if est_abonnement:
                jours_factures = 30
                # CORRECTION : Utilisation de Decimal('0.85') pour éviter le crash
                total_base = (vehicule.prix_par_jour * jours_factures) * Decimal('0.85')
                
                # Assurer la cohérence des dates
                if not reservation.date_debut:
                    reservation.date_debut = timezone.now().date()
                reservation.date_fin = reservation.date_debut + datetime.timedelta(days=30)
            else:
                # Mode standard basé sur l'intervalle de dates choisi
                # NOTE : Si l'input date_fin était 'disabled' côté client au moment du clic sur l'abonnement,
                # il n'est pas envoyé en POST. Mais comme on est dans le bloc 'else', l'abonnement n'est pas coché,
                # donc l'input est bien actif et sa valeur est présente.
                delta_jours = (reservation.date_fin - reservation.date_debut).days
                jours_factures = delta_jours if delta_jours > 0 else 1
                total_base = vehicule.prix_par_jour * jours_factures
            
            # --- AJOUT DU CHAUFFEUR FACTURÉ PAR JOUR ---
            reservation.inclut_chauffeur = avec_chauffeur
            if avec_chauffeur:
                # CORRECTION : Conversion du tarif du chauffeur en Decimal
                total_base += (Decimal('10000') * jours_factures)
                
            # Attribution du prix total calculé au modèle (transtypé en int si votre modèle attend un IntegerField)
            reservation.prix_total = int(total_base)
            
            # Vérification des conflits sur des dates identiques (uniquement pour les réservations payées)
            overlapping = Reservation.objects.filter(
                vehicule=vehicule,
                statut_paiement="paid",
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

    return render(request, 'reservation.html', {
        'form': form,
        'vehicule': vehicule
    })

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


# --- ÉTAPES DU PAIEMENT SIMULÉ DYNAMIQUE ---
@login_required
def page_paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, "paiement.html", {"reservation": reservation})

@login_required
def initier_paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        moyen = request.POST.get("moyen_paiement", "Inconnu")

        # Validation de simulation selon le choix (Carte vs Mobile)
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

        # Simulation d'une validation instantanée réussie
        transaction = "PIZ-" + uuid.uuid4().hex[:12].upper()

        reservation.transaction_id = transaction
        reservation.statut_paiement = "paid"
        reservation.status = "confirmed"
        reservation.save()

        # Envoi du message flash de confirmation
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
