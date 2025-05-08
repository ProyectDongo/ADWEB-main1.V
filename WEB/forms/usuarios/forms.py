from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from WEB.models import Usuario, RegistroEmpresas, Horario, Turno, RegistroEntrada, VigenciaPlan
from WEB.views.scripts import validar_rut, format_rut, mobile_validator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password


class AdminForm(UserCreationForm):
    rut = forms.CharField(
        max_length=12,
        validators=[validar_rut],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label="RUT"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,
        label="Email"
    )
    celular = forms.CharField(
        validators=[mobile_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 912345678'}),
        required=True,
        label="Celular"
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label="Grupos de Permisos"
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_permisos'}),
        required=False,
        label="Permisos Individuales"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'email', 'celular', 'password1', 'password2', 'grupos', 'permisos','first_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={' articles': 'form-control'}),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)
        return format_rut(rut)

    def clean_celular(self):
        celular = self.cleaned_data.get('celular', '').replace(' ', '')
        if not celular:
            raise forms.ValidationError("El celular es obligatorio.")
        return celular

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        user.rut = self.cleaned_data['rut']
        user.email = self.cleaned_data['email']
        user.celular = self.cleaned_data['celular']
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['grupos'])
            user.user_permissions.set(self.cleaned_data['permisos'])
        return user

















class SupervisorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vigencia_plan = forms.ModelChoiceField(
        queryset=VigenciaPlan.objects.none(),  # Inicialmente vacío
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Vigencia del Plan"
    )
    rut = forms.CharField(
        max_length=12,
        validators=[validar_rut],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label="RUT"
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label="Nombres"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,
        label="Email"
    )
    celular = forms.CharField(
        validators=[mobile_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 912345678'}),
        required=True,
        label="Celular"
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_grupos'}),
        required=False,
        label="Grupos de Permisos"
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_permisos'}),
        required=False,
        label="Permisos Individuales"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'email', 'celular', 'password1', 'password2', 'empresa', 'vigencia_plan', 'grupos', 'permisos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.role != 'admin':
                self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
                self.fields['empresa'].initial = user.empresa
                self.fields['vigencia_plan'].queryset = VigenciaPlan.objects.filter(empresa=user.empresa)
                self.fields['grupos'].queryset = user.groups.all()
                self.fields['permisos'].queryset = Permission.objects.filter(
                    id__in=user.user_permissions.values_list('id', flat=True)
                )
            else:
                self.fields['vigencia_plan'].queryset = VigenciaPlan.objects.all()
                self.fields['grupos'].queryset = Group.objects.all()
                self.fields['permisos'].queryset = Permission.objects.all()

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)
        return format_rut(rut)

    def clean_celular(self):
        celular = self.cleaned_data.get('celular', '').replace(' ', '')
        if not celular:
            raise forms.ValidationError("El celular es obligatorio.")
        return celular

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.role = 'supervisor'
        usuario.rut = self.cleaned_data['rut']
        usuario.email = self.cleaned_data['email']
        usuario.celular = self.cleaned_data['celular']
        usuario.empresa = self.cleaned_data['empresa']
        usuario.vigencia_plan = self.cleaned_data['vigencia_plan']
        if commit:
            usuario.save()
            usuario.groups.set(self.cleaned_data['grupos'])
            usuario.user_permissions.set(self.cleaned_data['permisos'])
        return usuario





















class TrabajadorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    vigencia_plan = forms.ModelChoiceField(
        queryset=VigenciaPlan.objects.none(),  # Inicialmente vacío
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Vigencia del Plan"
    )
    rut = forms.CharField(
        max_length=12,
        validators=[validar_rut],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label="RUT"
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        label="Nombres"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True,
        label="Email"
    )
    celular = forms.CharField(
        validators=[mobile_validator],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 912345678'}),
        required=True,
        label="Celular"
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_grupos'}),
        required=False,
        label="Grupos de Permisos"
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_permisos'}),
        required=False,
        label="Permisos Individuales"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'email', 'celular', 'password1', 'password2', 'empresa', 'grupos', 'permisos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.role != 'admin':
                self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
                self.fields['empresa'].initial = user.empresa
                self.fields['grupos'].queryset = user.groups.all()
                self.fields['permisos'].queryset = Permission.objects.filter(
                    id__in=user.user_permissions.values_list('id', flat=True)
                )
            else:
                self.fields['grupos'].queryset = Group.objects.all()
                self.fields['permisos'].queryset = Permission.objects.all()

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)
        return format_rut(rut)

    def clean_celular(self):
        celular = self.cleaned_data.get('celular', '').replace(' ', '')
        if not celular:
            raise forms.ValidationError("El celular es obligatorio.")
        return celular

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.role = 'trabajador'
        usuario.rut = self.cleaned_data['rut']
        usuario.email = self.cleaned_data['email']
        usuario.celular = self.cleaned_data['celular']
        usuario.empresa = self.cleaned_data['empresa']
        usuario.vigencia_plan = self.cleaned_data['vigencia_plan']
        if commit:
            usuario.save()
            usuario.groups.set(self.cleaned_data['grupos'])
            usuario.user_permissions.set(self.cleaned_data['permisos'])
        return usuario
    













    
class TrabajadorEditForm(UserChangeForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grupos de Permisos"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'grupos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.role == 'admin':
                self.fields['grupos'].queryset = Group.objects.all()
            else:
                self.fields['grupos'].queryset = user.groups.all()
            self.fields['grupos'].initial = self.instance.groups.all()











#-----------------------------------------------------------------------------------#
# PARA EL supervisor:
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper




class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una contraseña segura'
        }),
        required=False,
        help_text="Dejar en blanco para no cambiar la contraseña existente."
    )
    
    role = forms.ChoiceField(
        label="Rol",
        choices=Usuario.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Seleccione el tipo de usuario"
    )
    
    celular = forms.CharField(
        label="Número de celular",
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678'
        }),
        help_text="Número con código de país ej: +56912345678"
    )

    horario = forms.ModelChoiceField(
        queryset=Horario.objects.all(),
        label="Horario",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Seleccione el horario asignado al usuario"
    )

    turno = forms.ModelChoiceField(
        queryset=Turno.objects.all(),
        label="Turno",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Seleccione el turno asignado al usuario"
    )

    metodo_registro_permitido = forms.ChoiceField(
        label="Método de Registro Permitido",
        choices=Usuario.METODOS_REGISTRO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Seleccione el método de registro permitido para este usuario"
    )

    class Meta:
        model = Usuario
        # Eliminamos 'password' de fields para que no se asigne directamente al modelo
        fields = ['rut', 'username', 'first_name', 'last_name', 
                  'email', 'celular', 'role', 'horario', 'turno', 'metodo_registro_permitido']
        
        labels = {
            'username': 'Nombre de usuario',
            'rut': 'RUT',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }
        
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'rut': 'Formato: 12345678-9',
        }
        
        widgets = {
             'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario123'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678-9'
            }),
           
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Juan Antonio'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pérez González'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'userForm'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))
        self.fields['username'].help_text = "Requerido. Letras, números y @/./+/-/_"
        self.fields['rut'].widget.attrs['data-validation-url'] = '/usuarios/validate/'
        self.fields['email'].widget.attrs['data-validation-url'] = '/usuarios/validate/'
        if self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Contraseña requerida para nuevo usuario'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        queryset = Usuario.objects.filter(rut__iexact=rut)
        
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise forms.ValidationError("Este RUT ya está registrado en el sistema.")
            
        if not self.validate_rut(rut):
            raise forms.ValidationError("Formato de RUT inválido. Use: 12345678-9")
            
        return rut.upper()

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        queryset = Usuario.objects.filter(username__iexact=username)
        
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
            
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        queryset = Usuario.objects.filter(email__iexact=email)
        
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
            
        return email

   
    
    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if not celular:
            return celular
            
        if len(celular) < 9:
            raise ValidationError("El número debe tener al menos 9 dígitos")
            
        if not celular.startswith('+'):
            raise ValidationError("Debe incluir código de país. Ej: +56 9 1234 5678")
            
        return celular

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    @staticmethod
    def validate_rut(rut):
        return len(rut) >= 9 and '-' in rut









#formulariio para crear un horario
class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['nombre', 'hora_entrada', 'hora_salida', 'tolerancia_retraso', 'tolerancia_horas_extra','tipo_horario']
        widgets = {
            
            
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Horario Diurno'
            }),
            'tolerancia_retraso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 20',
                'min': 0,
                'max': 60
            }),
            'tolerancia_horas_extra': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 20',
                'min': 0,
                'max': 60
            }),
            'hora_entrada': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_salida': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'tipo_horario': forms.Select(attrs={
                'class': 'form-control'
            }),
            
        }
         
        





#formulario para crear un turno

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['nombre', 'dias_trabajo', 'dias_descanso', 'inicio_turno']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Turno 1'
            }),
            'dias_trabajo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 5',
                'min': 1,
                'max': 30
            }),
            'dias_descanso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2',
                'min': 1,
                'max': 30
            }),
            'inicio_turno': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

        }







class RegistroEntradaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['hora_entrada', 'hora_salida', 'metodo', 'latitud', 'longitud', 'precision', 'es_retraso', 'minutos_retraso', 'es_horas_extra', 'minutos_horas_extra']
        widgets = {
            'hora_entrada': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'hora_salida': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'latitud': forms.NumberInput(attrs={'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'step': 'any'}),
            'precision': forms.NumberInput(attrs={'step': 'any'}),
            'es_retraso': forms.CheckboxInput(),
            'minutos_retraso': forms.NumberInput(attrs={'seg': 0}),
            'es_horas_extra': forms.CheckboxInput(),
            'minutos_horas_extra': forms.NumberInput(attrs={'min': 0}),
        }
        exclude = ['hora_entrada','minutos_horas_extra','es_horas_extra','minutos_retraso']




class RegistroForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['hora_salida', 'es_retraso', 'minutos_retraso', 'es_horas_extra', 'minutos_horas_extra']
        widgets = {
            'hora_salida': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'es_retraso': forms.CheckboxInput(),
            'minutos_retraso': forms.NumberInput(attrs={'min': 0}),
            'es_horas_extra': forms.CheckboxInput(),
            'minutos_horas_extra': forms.NumberInput(attrs={'min': 0}),
        }