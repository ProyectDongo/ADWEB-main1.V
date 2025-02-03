from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Usuario, RegistroEmpresas, RegistroPermisos,RegistroEntrada


# forms para los registros de empresas 
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = RegistroEmpresas
        fields = ['rut', 'nombre', 'direccion', 'telefono']

#forms para los registros de permisos
class PermisoForm(forms.ModelForm):
    class Meta:
        model = RegistroPermisos
        fields = ['nombre', 'descripcion']

#forms para los registros de usuarios admin
class AdminForm(UserCreationForm):
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2', 'permisos']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
            self.save_m2m()  # Guarda los permisos (relación ManyToMany)
        return user

#forms para los registros de usuarios supervisor
class SupervisorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SupervisorForm, self).__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()
    
#forms para los registros de usuarios trabajador
class TrabajadorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TrabajadorForm, self).__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()
#forms para editar usuarios    
class AdminEditForm(UserChangeForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

#forms para editar usuarios
class SupervisorEditForm(UserChangeForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SupervisorEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permisos'].initial = self.instance.permisos.all()
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()

#forms para editar usuarios
class TrabajadorEditForm(UserChangeForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TrabajadorEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permisos'].initial = self.instance.permisos.all()
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()
#forms para los registros de entrada y salida
class RegistroEntradaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = []
class RegistroSalidaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = []


class LimiteEmpresaForm(forms.ModelForm):
    class Meta:
        model = RegistroEmpresas
        fields = ['limite_supervisores', 'limite_trabajadores']
        widgets = {
            'limite_supervisores': forms.NumberInput(attrs={'class': 'form-control'}),
            'limite_trabajadores': forms.NumberInput(attrs={'class': 'form-control'}),
        }