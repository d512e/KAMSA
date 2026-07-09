from django import forms
from .models import Reservation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client

class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse Email")
    telephone = forms.CharField(max_length=15, required=True, label="Numéro de Téléphone")
    permis_conduire = forms.FileField(required=True, label="Photo du Permis de conduire")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_debut', 'date_fin']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("date_debut")
        end = cleaned_data.get("date_fin")

        if start and end and start >= end:
            raise forms.ValidationError("La date de fin doit être après la date de début")

        return cleaned_data
    

class ProfilForm(forms.ModelForm):
    telephone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']