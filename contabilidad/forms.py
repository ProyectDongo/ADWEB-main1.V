from django import forms
from contabilidad.models import Transaccion

# FORMULARIOS DE PAGO ----------------------------------------------------------------------------------
class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['fecha', 'descripcion', 'tipo', 'monto']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
        }



# FIN DE FORMULARIOS DE PAGO ----------------------------------------------------------------------------------