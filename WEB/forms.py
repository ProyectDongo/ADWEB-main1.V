from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Usuario, RegistroEmpresas, RegistroPermisos,RegistroEntrada, VigenciaPlan, Plan,Provincia, Comuna, Region



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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provincia'].queryset = Provincia.objects.none()
        self.fields['comuna'].queryset = Comuna.objects.none()

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['provincia'].queryset = Provincia.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['provincia'].queryset = self.instance.region.provincia_set.all()

        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['comuna'].queryset = Comuna.objects.filter(provincia_id=provincia_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['comuna'].queryset = self.instance.provincia.comuna_set.all()
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

# las formas de los planes y empresas
class PlanVigenciaForm(forms.ModelForm):
    precio_original = forms.IntegerField(required=True)  # Añadir este campo
    indefinido = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Plan Indefinido'
    )

    class Meta:
        model = VigenciaPlan
        fields = ['empresa', 'plan', 'fecha_inicio', 'fecha_fin', 'indefinido', 'descuento']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '1'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_fin'].required = False

    def clean(self):
        cleaned_data = super().clean()
        indefinido = cleaned_data.get('indefinido')
        fecha_fin = cleaned_data.get('fecha_fin')
        descuento = cleaned_data.get('descuento')

        if indefinido and fecha_fin:
            raise forms.ValidationError("No puede tener fecha fin si el plan es indefinido")

        if descuento is not None and (descuento < 0 or descuento > 100):
            raise forms.ValidationError("El descuento debe estar entre 0 y 100")

        return cleaned_data