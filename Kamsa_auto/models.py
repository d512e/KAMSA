from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
# Create your models here.

class Vehicule(models.Model):
    nom = models.CharField(max_length=100)
    marque = models.CharField(max_length=100)
    prix_par_jour = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicules/', blank=True, null= True)

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

    def clean(self):
        if self.date_debut >= self.date_fin:
            raise ValidationError("La date de fin doit être après la date de début")

        overlapping = Reservation.objects.filter(
            vehicule=self.vehicule,
            date_debut__lt=self.date_fin,
            date_fin__gt=self.date_debut
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError("Ce véhicule est déjà réservé sur cette période")

    def __str__(self):
        return f"{self.user.username} - {self.vehicule.nom}"
    
    


