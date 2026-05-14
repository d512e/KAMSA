from django.contrib import admin
from .models import Vehicule, Reservation

# Register your models here.

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'marque', 'prix_par_jour', 'disponible')
    list_filter = ('disponible', 'marque')
    search_fields = ('nom', 'marque')
    list_editable = ('disponible', 'prix_par_jour')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicule', 'date_debut', 'date_fin', 'status')
    list_filter = ('status', 'date_debut')
    search_fields = ('user__username', 'vehicule__nom')
    autocomplete_fields = ('user', 'vehicule')