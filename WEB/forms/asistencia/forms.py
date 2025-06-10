from django import forms
from WEB.models import *
from ModuloAsistencia.models import RegistroEntrada

class RegistroEntradaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['metodo', 'firma_digital']
        
    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')
        
        if metodo == 'geo':
            lat = self.data.get('latitud')
            lon = self.data.get('longitud')
            
            if not lat or not lon:
                raise forms.ValidationError("Debe habilitar la geolocalización")
                
            # Validar precisión mínima
            precision = float(self.data.get('precision', 100))
            if precision > 50:  # 50 metros máximo de error
                raise forms.ValidationError("Precisión de ubicación insuficiente")
            
class RegistroSalidaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['metodo']