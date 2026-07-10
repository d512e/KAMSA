from django.contrib import admin
from .models import Vehicule, Reservation, ContacteMessage

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





# --- OU BIEN (Optionnel mais recommandé) ---
# Une configuration plus propre pour voir directement les messages sous forme de tableau :
@admin.register(ContacteMessage)
class ContacteMessageAdmin(admin.ModelAdmin):
    # Les colonnes à afficher dans la liste
    list_display = ('nom_complet', 'email', 'sujet', 'created_at')
    
    # Les filtres disponibles sur le côté droit
    list_filter = ('sujet', 'created_at')
    
    # La barre de recherche pour chercher par nom ou email
    search_fields = ('nom_complet', 'email', 'message')
    
    # Rendre les champs du message lisibles uniquement (pour ne pas les modifier par erreur)
    readonly_fields = ('created_at',)
