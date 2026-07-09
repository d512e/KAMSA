from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
# Create your models here.

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=15, unique=True)
    # AJOUT : Champ pour le fichier du permis de conduire
    permis_conduire = models.FileField(
        upload_to='permis/', 
        blank=False, 
        null=True, # null=True temporaire pour ne pas bloquer les comptes existants
        help_text="Fichier du permis de conduire (PDF, JPG, PNG)"
    )

    def __str__(self):
        return self.user.username

class Vehicule(models.Model):
    # Les choix disponibles en base de données
    CATEGORIE_CHOICES = [
        ('economique', 'Économique'),
        ('suv', 'SUV et 4x4'),
        ('utilitaire', 'Utilitaires'),
        ('luxe', 'Luxe'),
    ]

    nom = models.CharField(max_length=100)
    marque = models.CharField(max_length=100)
    prix_par_jour = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    # AJOUT DU CHAMP CATEGORIE :
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='economique')
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicules/', blank=True, null=True)

    def __str__(self):
        return f"{self.marque} - {self.nom}"
    

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]
    User = get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    inclut_chauffeur = models.BooleanField(default=False)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    STATUT_PAIEMENT = [
        ('unpaid', 'Non payé'),
        ('paid', 'Payé'),
        ('failed', 'Échoué'),
    ]
    statut_paiement = models.CharField(max_length=10, choices=STATUT_PAIEMENT, default='unpaid')
    transaction_id = models.CharField(max_length=100, blank=True, null=True) # ID fourni par l'API de paiement

    def __str__(self):
        return f"{self.user.username} - {self.vehicule.nom}"


