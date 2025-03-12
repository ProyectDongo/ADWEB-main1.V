import re
from django import forms


class PermisoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de permisos de usuario.
    
    Attributes:
        Meta.model (RegistroPermisos): Modelo asociado al formulario
        Meta.fields (list): Campos a incluir ['nombre', 'descripcion']
        Meta.widgets (dict): Configuración de widgets para cada campo
    """
    class Meta:
        
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
