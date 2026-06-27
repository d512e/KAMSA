from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='accueil'),
    path('vehicules', views.liste_vehicule, name='vehicules'),
    path('reservation', views.reservation, name='reservation'),
    path('reservation/<int:vehicule_id>/', views.reservation_vehicule, name='reservation_vehicule'),
    path('success/', views.booking_success, name='booking_success'),
    path('connexion/', views.connexion, name='connexion'),
    path('contact', views.contact, name='contact'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='connexion'), name='deconnexion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    
]