from django import forms
from .models import VigenciaPlan

class VigenciaPlanForm(forms.ModelForm):
    class Meta:
        model = VigenciaPlan
        fields = '__all__'  # Include all fields from the model