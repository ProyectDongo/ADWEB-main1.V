from django import forms
from inventario.models import ItemInventario

class ItemInventarioForm(forms.ModelForm):
    class Meta:
        model = ItemInventario
        fields = ['nombre', 'codigo', 'categoria', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }