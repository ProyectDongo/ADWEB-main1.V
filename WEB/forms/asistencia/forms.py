from django import forms
from WEB.models import *

class RegistroEntradaForm(forms.ModelForm):
    """
    Formulario base para registro de entradas (actualmente vacío).
    
    Nota: Campos definidos en la vista mediante lógica de negocio.
    """
    class Meta:
        model = RegistroEntrada
        fields = []

class RegistroSalidaForm(forms.ModelForm):
    """
    Formulario base para registro de salidas (actualmente vacío).
    
    Nota: Campos definidos en la vista mediante lógica de negocio.
    """
    class Meta:
        model = RegistroEntrada
        fields = []
