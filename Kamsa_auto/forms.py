from django import forms
from .models import Reservation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class InscriptionForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


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