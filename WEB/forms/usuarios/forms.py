import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from WEB.models.usuarios.usuario import Usuario
from WEB.models.empresa.empresa import RegistroEmpresas
from WEB.models.secure.permisos import RegistroPermisos
from WEB.views.scripts import *

class AdminForm(UserCreationForm):
    """
    Formulario especializado para creación de administradores.
    
    Hereda de UserCreationForm y añade:
        - Asignación automática de rol 'admin'
        - Otorgamiento de todos los permisos existentes
    
    Attributes:
        Meta.model (Usuario): Modelo de usuario
        Meta.fields (list): Campos del formulario
        Meta.widgets (dict): Configuración de widgets para campos de contraseña
    
    Methods:
        save: Guarda el usuario con rol y permisos adecuados
    """
    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        """
        Guarda el usuario administrador con todos los permisos.
        
        Args:
            commit (bool): Determina si guardar en la base de datos
        
        Returns:
            Usuario: Instancia del usuario administrador creado
        
        Behavior:
            - Establece el rol como 'admin'
            - Asigna todos los permisos existentes
            - Guarda relaciones many-to-many
        """
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
            user.permisos.set(RegistroPermisos.objects.all())
            self.save_m2m()
        return user

class SupervisorForm(UserCreationForm):
    """
    Formulario para creación de supervisores con permisos limitados.
    """
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),  # Inicialmente vacío, se completa en __init__
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_permisos'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'nombre', 'last_name', 'apellidoM', 'celular', 'email', 'password1', 'password2', 'empresa', 'permisos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidoM': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    celular = forms.CharField(
        validators=[mobile_validator],
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 912345678',
            'maxlength': '12'
        })
    )

    def clean_celular(self):
        celular = self.cleaned_data.get('celular', '').replace(' ', '')
        return celular if celular else None

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Realiza la validación (se asume que validar_rut lanza una excepción si es inválido)
        validar_rut(rut)
        # Devuelve el RUT formateado
        return format_rut(rut)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.role = 'supervisor'
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario


class TrabajadorForm(UserCreationForm):
    """
    Formulario para creación de trabajadores con restricciones de empresa.
    """
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),  # Inicialmente vacío, se completa en __init__
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_permisos'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'nombre', 'last_name', 'apellidoM', 'celular', 'email', 'password1', 'password2', 'empresa', 'permisos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidoM': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    celular = forms.CharField(
        validators=[mobile_validator],
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 912345678',
            'maxlength': '12'
        })
    )

    def clean_celular(self):
        celular = self.cleaned_data.get('celular', '').replace(' ', '')
        return celular if celular else None

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)
        return format_rut(rut)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'trabajador'
        if commit:
            user.save()
            self.save_m2m()
        return user


class AdminEditForm(UserChangeForm):
    """
    Formulario para edición de administradores con gestión de permisos.
    
    Attributes:
        empresa (ModelChoiceField): Selector de empresa asociada
        permisos (ModelMultipleChoiceField): Selector de permisos
    """
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

class SupervisorEditForm(UserChangeForm):
    """
    Formulario para edición de supervisores con restricciones de permisos.
    
    Attributes:
        empresa (ModelChoiceField): Selector de empresa asociada
        permisos (ModelMultipleChoiceField): Selector de permisos
    
    Methods:
        __init__: Configura los permisos disponibles según el editor
    """
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con restricciones de permisos.
        
        Args:
            user (Usuario): Usuario que realiza la edición
        
        Behavior:
            - Establece permisos iniciales del usuario
            - Restringe permisos disponibles según el rol del editor
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permisos'].initial = self.instance.permisos.all()
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()

class TrabajadorEditForm(UserChangeForm):
    """
    Formulario para edición de trabajadores con gestión de permisos.
    
    Attributes:
        empresa (ModelChoiceField): Selector de empresa asociada
        permisos (ModelMultipleChoiceField): Selector de permisos
    
    Methods:
        __init__: Configura los permisos disponibles según el editor
    """
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con restricciones de permisos.
        
        Args:
            user (Usuario): Usuario que realiza la edición
        
        Behavior:
            - Establece permisos iniciales del usuario
            - Restringe permisos disponibles según el rol del editor
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permisos'].initial = self.instance.permisos.all()
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()