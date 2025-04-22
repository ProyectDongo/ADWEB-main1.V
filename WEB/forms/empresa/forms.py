import re
from django import forms
from django.utils.safestring import mark_safe
from WEB.views.scripts import *
from WEB.models import *









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
