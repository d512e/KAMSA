from django import forms
from .models import Reservation

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