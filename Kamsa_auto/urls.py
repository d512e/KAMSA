from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='accueil'),
    path('vehicules', views.liste_vehicule, name='vehicules'),
    path('reservation', views.reservation, name='reservation'),
    path('reservation/<int:vehicule_id>/', views.reservation_vehicule, name='reservation_vehicule'),
    path('success/', views.booking_success, name='booking_success'),
    path('compte', views.compte, name='compte'),
    path('contact', views.contact, name='contact'),
    
]