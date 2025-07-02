from django import forms
import re
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from django.utils.safestring import mark_safe
from WEB.models import RegistroEmpresas,VigenciaPlan,Plan
from users.models import Usuario
from geografia.models import Provincia,Comuna
from users.validators import validar_rut,mobile_validator,format_rut,phone_validator



#INDICE :
# 1. FORMULARIO DE CREACION DE ADMINISTRADORES DE LINEA 14 A LINEA 81

# 2. FORMULARIO DE CREACION DE SUPERVISORES DE LINEA 87 A LINEA 189

# 3. FORMULARIO DE CREACION DE TRABAJADORES DE LINEA 214 A LINEA 314

# 4. FORMULARIO DE EDICION DE TRABAJADORES DE LINEA 322 A LINEA 353

# 5. FORMULARIO DE CREACION DE EMPRESAS DE LINEA 368 A LINEA 541

# 6. FORMULARIO DE CREACION DE VIGENCIAS PARA EMPRESAS DE LINEA 547 A LINEA 660

# 7. FORMULARIO DE CREACION DE PLANES DE LINEA 669 A LINEA 696

# 8. FORMULARIO DE CREACION DE TRANSACCIONES DE PAGO DE LINEA 699 A LINEA 713




# CREACION DE ADMIN -----------------------------------------------------------


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

#FIN DE CREACION DE ADMIN -----------------------------------------------------------





# CREAR SUPERVISORES -----------------------------------------------------------


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

#FIN DE CREAR SUPERVISORES -----------------------------------------------------------

















#CREAR TRABAJADORES -----------------------------------------------------------

class TrabajadorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    vigencia_plan = forms.ModelChoiceField(
        queryset=VigenciaPlan.objects.none(),  
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
    
#FIN DE CREAR TRABAJADORES -----------------------------------------------------------







# EDITAR USUARIOS -----------------------------------------------------------


    
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

# FIN DE EDITAR USUARIOS -----------------------------------------------------------



# CREACION  DE EMPRESAS  -----------------------------------------------------------



class EmpresaForm(forms.ModelForm):
    """
    Formulario completo para el registro y modificación de empresas.
    
    Hereda de ModelForm y utiliza el modelo RegistroEmpresas.
    Implementa lógica dinámica para selección de ubicación geográfica.
    """
    class Meta:
        model = RegistroEmpresas
        fields = [
            'codigo_cliente', 'rut', 'nombre', 'giro', 'direccion', 'numero', 'oficina',
            'region', 'provincia', 'comuna', 'telefono', 'celular',
            'email', 'web', 'vigente', 'estado', 'rut_representante',
            'nombre_representante', 'nombre_contacto', 'celular_contacto',
            'mail_contacto',
        ]
        widgets = {
            'codigo_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Cliente'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT Empresa formato: 12345678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón Social'}),
            'giro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Giro Comercial'}),
            'telefono':
              forms.TextInput(attrs={
                  'class': 'form-control',  
                  'inputmode': 'numeric', 
                  'placeholder': 'Teléfono Fijo',
                  'onkeypress': "return /[0-9\\+\\s]/.test(event.key);",}),


            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Corporativo'}),
            'web': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sitio Web'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'provincia': forms.Select(attrs={'class': 'form-control'}),
            'comuna': forms.Select(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Dirección'}),
            'numero': 
            forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Número',
                'inputmode': 'numeric', 
                'onkeypress': "return /[0-9\\+\\s]/.test(event.key);"}),

            'oficina': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Oficina'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'vigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'plan_contratado': forms.Select(attrs={'class': 'form-control'}),
            'rut_representante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ingrese rut = 12344461-2'}),
            'nombre_representante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Representante'}),
        }

    telefono = forms.CharField(
        validators=[phone_validator],
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 221234567',
            'maxlength': '12',
            'inputmode': 'numeric',
            'onkeypress': "return /[0-9\\+\\s]/.test(event.key);"
        })
    )

    celular_contacto = forms.CharField(
        validators=[mobile_validator],
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 912345678',
            'maxlength': '12',
            'inputmode': 'numeric',
            'onkeypress': "return /[0-9\\+\\s]/.test(event.key);"
        })
    )
   
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').replace(' ', '')
        return telefono if telefono else None

    def clean_celular_contacto(self):
        celular = self.cleaned_data.get('celular_contacto', '').replace(' ', '')
        return celular if celular else None

    def format_rut(self, rut):
        """
        Formatea un RUT para que se guarde con puntos y guion.
        Ejemplo: "765432103" -> "76.543.210-3"
        """
        if not rut:
            return rut
        # Eliminamos puntos, guiones y espacios
        cleaned = re.sub(r'[\.\-\s]', '', rut).upper()
        if len(cleaned) < 2:
            return rut  # No se puede formatear correctamente
        check_digit = cleaned[-1]
        number_part = cleaned[:-1]
        try:
            # Formateamos la parte numérica con separador de miles (usando punto)
            formatted_number = "{:,}".format(int(number_part)).replace(",", ".")
        except ValueError:
            formatted_number = number_part
        return f"{formatted_number}-{check_digit}"
   

    @staticmethod
    def normalize_rut(rut):
        """
        Normaliza un RUT removiendo puntos, guiones y espacios, y convirtiendo a mayúsculas.
        """
        return re.sub(r'[\.\-\s]', '', rut).upper() if rut else rut

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Valida el RUT (si es inválido, validar_rut() lanza excepción)
        validar_rut(rut)
        formatted = self.format_rut(rut)
        normalized = self.normalize_rut(formatted)
        qs = RegistroEmpresas.objects.all()
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        for empresa in qs:
            if self.normalize_rut(empresa.rut) == normalized:
                raise forms.ValidationError("Ya existe una empresa con este RUT.")
        return formatted

    def clean_rut_representante(self):
        rut = self.cleaned_data.get('rut_representante')
        validar_rut(rut)
        return self.format_rut(rut)

    def clean(self):
        cleaned_data = super().clean()
        rut_empresa = cleaned_data.get('rut')
        rut_representante = cleaned_data.get('rut_representante')
        if rut_empresa and rut_representante:
            if self.normalize_rut(rut_empresa) == self.normalize_rut(rut_representante):
                raise forms.ValidationError(
                    "El RUT de empresa y el RUT del representante no pueden ser el mismo."
                )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con querysets dinámicos para provincias y comunas.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.label = mark_safe(f"<strong>{field.label}</strong>")
            else:
                field.label = mark_safe(f"<strong>{field.label}</strong>")
            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'

        # Actualiza dinámicamente el queryset de provincias según la región seleccionada
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['provincia'].queryset = Provincia.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['provincia'].queryset = self.instance.region.provincia_set.all()

        # Actualiza dinámicamente el queryset de comunas según la provincia seleccionada
        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['comuna'].queryset = Comuna.objects.filter(provincia_id=provincia_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['comuna'].queryset = self.instance.provincia.comuna_set.all()


#FIN DE CREACION DE EMPRESAS  -----------------------------------------------------------





#CREACION DE VIGENCIAS PARA EMPRESAS -----------------------------------------------------------
class PlanVigenciaForm(forms.ModelForm):
    """
    Formulario avanzado para gestión de vigencias de planes.

    Atributos:
        precio_original (DecimalField): Representa el precio original (se guarda en `monto_plan`).
        indefinido (BooleanField): Indica si el plan no tiene fecha fin.
        precio_final (DecimalField): Campo de solo lectura que muestra el monto final (almacenado en `monto_final`).
    """
    precio_original = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Precio Original",
        help_text="Precio base del plan sin descuentos"
    )
    indefinido = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Plan Indefinido',
        help_text="Marcar si el plan no tiene fecha de expiración"
    )
    precio_final = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Precio Final",
        help_text="Precio final calculado aplicando el descuento"
    )

    class Meta:
        model = VigenciaPlan
        fields = ['empresa', 'plan', 'fecha_inicio', 'fecha_fin', 'descuento', 'codigo_plan',]
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'codigo_plan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del Plan'}),
            'fecha_inicio': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD'
                },
                format='%Y-%m-%d'
            ),
            'fecha_fin': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD'
                },
                format='%Y-%m-%d'
            ),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '1',
                'placeholder': '0-100%'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario inyectando valores iniciales desde la instancia,
        de forma que descuento, fecha_fin y precio_final (monto_final) se recuperen correctamente.
        """
        instance = kwargs.get('instance', None)
        if instance and instance.pk:
            initial = kwargs.setdefault('initial', {})
            initial['precio_original'] = instance.monto_plan
            initial['descuento'] = instance.descuento
            initial['fecha_fin'] = instance.fecha_fin.strftime('%Y-%m-%d') if instance.fecha_fin else ''
            initial['indefinido'] = instance.fecha_fin is None
            initial['precio_final'] = instance.monto_final
        super().__init__(*args, **kwargs)
        # Hacemos que fecha_fin sea opcional
        self.fields['fecha_fin'].required = False

    def clean(self):
        """
        Valida la coherencia entre campos.

        - Verifica que el descuento esté entre 0 y 100.
        - Si se asigna una fecha_fin, se fuerza 'indefinido' a False.
        """
        cleaned_data = super().clean()

        descuento = cleaned_data.get('descuento')
        if descuento is not None and not (0 <= descuento <= 100):
            raise forms.ValidationError("El descuento debe ser un porcentaje entre 0 y 100")

        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_fin:
            cleaned_data['indefinido'] = False

        return cleaned_data

    def save(self, commit=True):
        """
        Guarda la instancia actualizando:
        
        - 'monto_plan' con el valor de 'precio_original'.
        - Si se marca como indefinido, se establece 'fecha_fin' a None.
        """
        instance = super().save(commit=False)
        instance.monto_plan = self.cleaned_data.get('precio_original')
        if self.cleaned_data.get('indefinido'):
            instance.fecha_fin = None
        # Se asume que 'monto_final' ya se encuentra calculado en la instancia.
        if commit:
            instance.save()
        return instance

# FIN DE CREACION DE VIGENCIAS PARA EMPRESAS -----------------------------------------------------------








#CREACION DE PLANES -----------------------------------------------------------

class PlanForm(forms.ModelForm):
    """
    Formulario para crear y actualizar planes.
    """
    class Meta:
        model = Plan
        fields = ['nombre', 'max_usuarios','valor', 'codigo', 'activo','descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Plan'}),
            'max_usuarios': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Máximo de Usuarios'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor del Plan'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del Plan'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,'placeholder':'Breve descripcion'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del Plan',
            'max_usuarios': 'Máximo de usuarios',
            'valor': 'Valor del Plan',
            'codigo': 'Código del Plan',
            'descripciom':'descripcion del plan',
            'activo': 'Activo',
        }


# FIN DE CREACION DE PLANES  ----------------------------------------------------------------------------------



