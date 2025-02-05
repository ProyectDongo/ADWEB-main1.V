"""
Módulo de formularios para el sistema de gestión empresarial.

Contiene formularios para:
- Registro y edición de empresas
- Gestión de usuarios (admin, supervisores, trabajadores)
- Control de permisos
- Registro de entradas/salidas
- Configuración de planes y límites
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, RegistroEmpresas, RegistroPermisos, RegistroEntrada, VigenciaPlan, Plan, Provincia, Comuna, Region

class EmpresaForm(forms.ModelForm):
    """
    Formulario completo para el registro y modificación de empresas.
    
    Hereda de ModelForm y utiliza el modelo RegistroEmpresas.
    Implementa lógica dinámica para selección de ubicación geográfica.
    
    Attributes:
        Meta.model (RegistroEmpresas): Modelo asociado al formulario
        Meta.fields (list): Lista de todos los campos del modelo
        Meta.widgets (dict): Configuración personalizada de widgets para cada campo
    
    Methods:
        __init__: Inicializa los querysets dinámicos para provincias y comunas
    """
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
        """
        Inicializa el formulario con querysets dinámicos para provincias y comunas.
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos clave (incluye 'instance' para edición)
        
        Behavior:
            - Actualiza provincias basado en la región seleccionada
            - Actualiza comunas basado en la provincia seleccionada
            - Maneja tanto creación como edición de instancias
        """
        super().__init__(*args, **kwargs)
        self.fields['provincia'].queryset = Provincia.objects.none()
        self.fields['comuna'].queryset = Comuna.objects.none()

        # Lógica para actualización dinámica de provincias
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['provincia'].queryset = Provincia.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass  # Mantener queryset vacío si hay error en los datos
        elif self.instance.pk:
            self.fields['provincia'].queryset = self.instance.region.provincia_set.all()

        # Lógica para actualización dinámica de comunas
        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['comuna'].queryset = Comuna.objects.filter(provincia_id=provincia_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['comuna'].queryset = self.instance.provincia.comuna_set.all()

class PermisoForm(forms.ModelForm):
    """
    Formulario para la creación y edición de permisos de usuario.
    
    Attributes:
        Meta.model (RegistroPermisos): Modelo asociado al formulario
        Meta.fields (list): Campos a incluir ['nombre', 'descripcion']
        Meta.widgets (dict): Configuración de widgets para cada campo
    """
    class Meta:
        model = RegistroPermisos
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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
    
    Attributes:
        empresa (ModelChoiceField): Selector de empresa asociada
        permisos (ModelMultipleChoiceField): Selector múltiple de permisos
    
    Methods:
        __init__: Personaliza los querysets según el usuario creador
        save: Asigna el rol 'supervisor' al guardar
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
        fields = ['username', 'password1', 'password2', 'empresa', 'permisos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con restricciones de permisos y empresas.
        
        Args:
            user (Usuario): Usuario que crea el supervisor (obtenido de kwargs)
        
        Behavior:
            - Para no-admins: Restringe a su empresa y permisos asignados
            - Para admins: Permite todas las empresas y permisos
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()

    def save(self, commit=True):
        """Guarda el usuario con rol de supervisor y permisos asignados."""
        user = super().save(commit=False)
        user.role = 'supervisor'
        if commit:
            user.save()
            self.save_m2m()
        return user

class TrabajadorForm(UserCreationForm):
    """
    Formulario para creación de trabajadores con restricciones de empresa.
    
    Attributes:
        empresa (ModelChoiceField): Selector de empresa asociada
        permisos (ModelMultipleChoiceField): Selector múltiple de permisos
    
    Methods:
        __init__: Personaliza querysets según el usuario creador
        save: Asigna el rol 'trabajador' al guardar
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
        fields = ['username', 'password1', 'password2', 'empresa', 'permisos']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Configura los querysets de empresa y permisos.
        
        Args:
            user (Usuario): Usuario que crea el trabajador
        
        Behavior:
            - Para no-admins: Restringe a su empresa y permisos
            - Para admins: Permite todas las empresas y permisos
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields['empresa'].queryset = RegistroEmpresas.objects.filter(id=user.empresa.id)
            self.fields['permisos'].queryset = user.permisos.all()
        elif user and user.role == 'admin':
            self.fields['permisos'].queryset = RegistroPermisos.objects.all()

    def save(self, commit=True):
        """Guarda el usuario con rol de trabajador y permisos asignados."""
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

class LimiteEmpresaForm(forms.ModelForm):
    """
    Formulario para establecer límites de usuarios por empresa.
    
    Attributes:
        Meta.model (RegistroEmpresas): Modelo asociado
        Meta.fields (list): Campos de límites
        Meta.widgets (dict): Configuración de widgets numéricos
    """
    class Meta:
        model = RegistroEmpresas
        fields = ['limite_supervisores', 'limite_trabajadores']
        widgets = {
            'limite_supervisores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'limite_trabajadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
        }

class PlanVigenciaForm(forms.ModelForm):
    """
    Formulario avanzado para gestión de vigencias de planes.
    
    Attributes:
        precio_original (IntegerField): Campo adicional para precio base
        indefinido (BooleanField): Indicador de plan sin fecha fin
    
    Methods:
        __init__: Hace opcional el campo fecha_fin
        clean: Valida consistencia entre campos
    """
    precio_original = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Precio base del plan sin descuentos"
    )
    indefinido = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Plan Indefinido',
        help_text="Marcar si el plan no tiene fecha de expiración"
    )

    class Meta:
        model = VigenciaPlan
        fields = ['empresa', 'plan', 'fecha_inicio', 'fecha_fin', 'indefinido', 'descuento']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD'
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '1',
                'placeholder': '0-100%'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Hace opcional el campo fecha_fin durante la inicialización."""
        super().__init__(*args, **kwargs)
        self.fields['fecha_fin'].required = False

    def clean(self):
        """
        Valida la coherencia entre los campos del formulario.
        
        Raises:
            ValidationError: Si hay inconsistencia entre campos
        
        Returns:
            dict: Datos limpios y validados
        """
        cleaned_data = super().clean()
        indefinido = cleaned_data.get('indefinido')
        fecha_fin = cleaned_data.get('fecha_fin')
        descuento = cleaned_data.get('descuento')

        # Validación de plan indefinido
        if indefinido and fecha_fin:
            raise forms.ValidationError(
                "Un plan indefinido no puede tener fecha de finalización"
            )

        # Validación de rango de descuento
        if descuento is not None and not (0 <= descuento <= 100):
            raise forms.ValidationError(
                "El descuento debe ser un porcentaje entre 0 y 100"
            )

        return cleaned_data