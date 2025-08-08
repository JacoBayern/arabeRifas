from django import forms
from .models import Payment, Sorteo

class SorteoForm(forms.ModelForm):
    class Meta:
        model = Sorteo
        fields = '__all__'