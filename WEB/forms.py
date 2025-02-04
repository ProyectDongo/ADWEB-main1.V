from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Usuario, RegistroEmpresas, RegistroPermisos,RegistroEntrada


# forms para los registros de empresas 
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = RegistroEmpresas
        fields = [
            'rut', 'nombre', 'giro', 'direccion', 'numero', 'oficina',
            'region', 'provincia', 'comuna', 'telefono', 'celular',
            'email', 'web', 'vigente', 'estado', 'rut_representante',
            'nombre_representante', 'nombre_contacto', 'celular_contacto',
            'mail_contacto', 'plan_contratado'
        ]
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'giro': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'oficina': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'provincia': forms.Select(attrs={'class': 'form-control'}),
            'comuna': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'web': forms.URLInput(attrs={'class': 'form-control'}),
            'vigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'rut_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'mail_contacto': forms.EmailInput(attrs={'class': 'form-control'}),
            'plan_contratado': forms.Select(attrs={'class': 'form-control'}),
        }
#forms para los registros de permisos
class PermisoForm(forms.ModelForm):
    class Meta:
        model = RegistroPermisos
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }

#forms para los registros de usuarios admin
class AdminForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
            # Asignar todos los permisos personalizados existentes
            user.permisos.set(RegistroPermisos.objects.all())
            self.save_m2m()
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
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),  }

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
        wibgets = {
                'username': forms.TextInput(attrs={'class': 'form-control'}), }

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