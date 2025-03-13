from django import forms
from WEB.models import *

class RegistroEntradaForm(forms.ModelForm):
    METODO_CHOICES = [
        ('firma', 'Firma Digital'),
        ('huella', 'Huella Digital'),
        ('geo', 'Geolocalización'),
    ]
    
    metodo = forms.ChoiceField(
        choices=METODO_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = RegistroEntrada
        fields = ['metodo', 'firma_digital', 'huella_id', 'latitud', 'longitud']
        widgets = {
            'huella_id': forms.HiddenInput(),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')
        
        if metodo == 'firma' and not cleaned_data.get('firma_digital'):
            raise forms.ValidationError("Debe subir una firma digital")
            
        if metodo == 'huella' and not cleaned_data.get('huella_id'):
            raise forms.ValidationError("Error en la lectura de huella")
            
        if metodo == 'geo' and (not cleaned_data.get('latitud') or (not cleaned_data.get('longitud'))):
            raise forms.ValidationError("Geolocalización no detectada")
        
        return cleaned_data

class RegistroSalidaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['metodo']