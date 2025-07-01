from django import forms
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from WEB.models import *
from users.models import *
from ModuloAsistencia.models import RegistroEntrada
from django.forms import inlineformset_factory




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
        self.fields['role'].choices = [(k, v) for k, v in Usuario.ROLES if k != 'admin']
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
        celular = self.cleaned_data.get('celular', '').replace(' ', '')
        if not celular:
            raise forms.ValidationError("El celular es obligatorio.")
        return celular

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

    @staticmethod
    def validate_rut(rut):
        return len(rut) >= 9 and '-' in rut




class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_contrato': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sindicato': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso_sindicato': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'tipo_jornada': forms.TextInput(attrs={'class': 'form-control'}),
        }
class ContactoUsuarioForm(forms.ModelForm):
    class Meta:
        model = ContactoUsuario
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'dpto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InformacionBancariaForm(forms.ModelForm):
    class Meta:
        model = InformacionBancaria
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'tipo_cuenta': forms.Select(attrs={'class': 'form-control'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InformacionAdicionalForm(forms.ModelForm):
    class Meta:
        model = InformacionAdicional
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'fecha_primera_cotizacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'anos_anteriores': forms.NumberInput(attrs={'class': 'form-control'}),
            'meses_anteriores': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_vacaciones_usados': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_reconocimiento_vacaciones': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'dias_vacaciones_anuales': forms.NumberInput(attrs={'class': 'form-control'}),
            'ajustes_vacaciones_progresivas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SeguroCesantiaForm(forms.ModelForm):
    class Meta:
        model = SeguroCesantia
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'acogido_seguro': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'afp_recaudadora': forms.TextInput(attrs={'class': 'form-control'}),
            'sueldo_patronal': forms.NumberInput(attrs={'class': 'form-control'}),
            'acogido_seguro_accidentes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PrevisionForm(forms.ModelForm):
    class Meta:
        model = Prevision
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'salud': forms.Select(attrs={'class': 'form-control'}),
            'regimen': forms.Select(attrs={'class': 'form-control'}),
            'tasa': forms.NumberInput(attrs={'class': 'form-control'}),
            'afp': forms.Select(attrs={'class': 'form-control'}),
            'pensionado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OtrosForm(forms.ModelForm):
    class Meta:
        model = Otros
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'tipo_discapacidad': forms.TextInput(attrs={'class': 'form-control'}),
            'tasa_indemnizacion': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AntecedentesConducirForm(forms.ModelForm):
    class Meta:
        model = AntecedentesConducir
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'tipo_licencia': forms.TextInput(attrs={'class': 'form-control'}),
            'municipalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ultimo_control': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'hoja_vida_conducir': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

AntecedentesConducirFormSet = inlineformset_factory(
    Usuario, AntecedentesConducir,
    form=AntecedentesConducirForm,
    fields=['tipo_licencia', 'municipalidad', 'fecha_ultimo_control', 'fecha_vencimiento', 'hoja_vida_conducir'],
    widgets={
        'tipo_licencia': forms.TextInput(attrs={'class': 'form-control'}),
        'municipalidad': forms.TextInput(attrs={'class': 'form-control'}),
        'fecha_ultimo_control': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'hoja_vida_conducir': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    },
                                                   
    extra=1, can_delete=True
)

class NivelEstudiosForm(forms.ModelForm):
    class Meta:
        model = NivelEstudios
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'nivel_estudios': forms.TextInput(attrs={'class': 'form-control'}),
            'completo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ultimo_curso': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.TextInput(attrs={'class': 'form-control'}),
        }
NivelEstudiosFormSet = inlineformset_factory(
    Usuario, NivelEstudios,
    fields=('nivel_estudios', 'completo', 'ultimo_curso', 'carrera'),
    widgets={
        'nivel_estudios': forms.TextInput(attrs={'class': 'form-control'}),
        'completo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'ultimo_curso': forms.TextInput(attrs={'class': 'form-control'}),
        'carrera': forms.TextInput(attrs={'class': 'form-control'}),
    },
    extra=1, can_delete=True
)

class InformacionComplementariaForm(forms.ModelForm):
    class Meta:
        model = InformacionComplementaria
        fields = '__all__'
        exclude = ['usuario']
        widgets = {
            'pais_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'pasaporte': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_visa': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_calzado': forms.TextInput(attrs={'class': 'form-control'}),
            'talla_ropa': forms.TextInput(attrs={'class': 'form-control'}),
            'grupo_sanguineo': forms.TextInput(attrs={'class': 'form-control'}),
            'alergico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'personal_destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formsets para relaciones ForeignKey
ExamenesMutualFormSet = inlineformset_factory(
    Usuario, ExamenesMutual,
    fields=['tipo_examen', 'fecha_examen', 'fecha_vencimiento'],
    widgets={
        'tipo_examen': forms.TextInput(attrs={'class': 'form-control'}),
        'fecha_examen': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
    },
    extra=1, can_delete=True
)

GrupoFamiliarFormSet = inlineformset_factory(
    Usuario, GrupoFamiliar,
    fields=['rut_carga', 'nombre_carga', 'fecha_nacimiento', 'edad', 'sexo'],
    widgets={
        'rut_carga': forms.TextInput(attrs={'class': 'form-control'}),
        'nombre_carga': forms.TextInput(attrs={'class': 'form-control'}),
        'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'edad': forms.NumberInput(attrs={'class': 'form-control'}),
        'sexo': forms.Select(attrs={'class': 'form-control'}),
    },
    extra=1, can_delete=True
)

CapacitacionFormSet = inlineformset_factory(
    Usuario, Capacitacion,
    fields=['descripcion', 'horas', 'institucion'],
    widgets={
        'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        'horas': forms.NumberInput(attrs={'class': 'form-control'}),
        'institucion': forms.TextInput(attrs={'class': 'form-control'}),
    },
    extra=1, can_delete=True
)

LicenciasMedicasFormSet = inlineformset_factory(
    Usuario, LicenciasMedicas,
    fields=['tipo_accidente', 'clasificacion_accidente', 'fecha_inicio_reposo', 'fecha_termino', 'fecha_alta', 'dias_reposo'],
    widgets={
        'tipo_accidente': forms.TextInput(attrs={'class': 'form-control'}),
        'clasificacion_accidente': forms.TextInput(attrs={'class': 'form-control'}),
        'fecha_inicio_reposo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'fecha_alta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        'dias_reposo': forms.NumberInput(attrs={'class': 'form-control'}),
    },
    extra=1, can_delete=True
)






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
        fields = ['metodo', 'latitud', 'longitud', 'firma_digital']
        widgets = {
            'metodo': forms.Select(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'firma_digital': forms.FileInput(attrs={'class': 'form-control'}),
        }




class RegistroForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['hora_salida', 'metodo', 'latitud', 'longitud', 
            'firma_digital', 'huella_id', 'es_retraso', 
            'minutos_retraso', 'es_horas_extra', 'minutos_horas_extra']
        widgets = {
            'hora_salida': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'es_retraso': forms.CheckboxInput(),
            'minutos_retraso': forms.NumberInput(attrs={'min': 0}),
            'es_horas_extra': forms.CheckboxInput(),
            'minutos_horas_extra': forms.NumberInput(attrs={'min': 0}),
        }


class DiaHabilitadoForm(forms.ModelForm):
    class Meta:
        model = DiaHabilitado
        fields = ['fecha', 'habilitado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'habilitado': forms.CheckboxInput(),
        }







class GenerarAsignacionesForm(forms.Form):
    fecha_inicio = forms.DateField(
        label="Fecha Inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    fecha_fin = forms.DateField(
        label="Fecha Fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    tipo_rotacion = forms.ChoiceField(
        label="Tipo de Rotación",
        choices=[
            ('3_turnos_8h', 'Rotación 3 Turnos 8h'),
            ('12x36', '12×36 Horas'),
            ('2x2', '2×2 (2 días trabajo, 2 descanso) - Guardia'),
            ('2x3', '2×3 (2 días trabajo, 3 descanso) - Producción'),
            ('3x2', '3×2 (3 días trabajo, 2 descanso) - Vigilancia'),
            ('3x3', '3×3 (3 días trabajo, 3 descanso) - 24/7'),
            ('4x2', '4×2 (4 días trabajo, 2 descanso) - Operarios'),
            ('4x3', '4×3 (4 días trabajo, 3 descanso) - Guardia'),
            ('4x4', '4×4 (4 días trabajo, 4 descanso) - Minería'),
            ('5x1', '5×1 (5 días trabajo, 1 descanso) - Comprimido'),
            ('5x2', '5×2 (5 días trabajo, 2 descanso) - Oficina/Retail'),
            ('6x1', '6×1 (6 días trabajo, 1 descanso) - Excepcional'),
            ('6x2', '6×2 (6 días trabajo, 2 descanso) - Manufactura'),
            ('6x3', '6×3 (6 días trabajo, 3 descanso) - 24/7'),
            ('7x7', '7×7 (7 días trabajo, 7 descanso) - Minería camp.'),
            ('8x4', '8×4 (8 días trabajo, 4 descanso) - Faena interna'),
            ('8x8', '8×8 (8 días trabajo, 8 descanso) - Minería'),
            ('10x10', '10×10 (10 días trabajo, 10 descanso) - Minería camp.'),
            ('12x12', '12×12 (12 días trabajo, 12 descanso) - Guardia/Seguridad'),
            ('14x7', '14×7 (14 días trabajo, 7 descanso) - Minería remota'),
            ('14x14', '14×14 (14 días trabajo, 14 descanso) - Remoto'),
            ('21x7', '21×7 (21 días trabajo, 7 descanso) - Muy excepcional'),
            ('personalizado', 'Rotación Personalizada'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    horarios = forms.ModelMultipleChoiceField(
        label="Horarios",
        queryset=Horario.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Seleccione uno o más horarios. Se aplicarán en orden cíclico durante los días de trabajo."
    )
    dias_trabajo = forms.IntegerField(
        label="Días de Trabajo (X)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        required=False,
        help_text="Número de días consecutivos de trabajo para la rotación personalizada."
    )
    dias_descanso = forms.IntegerField(
        label="Días de Descanso (Y)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        required=False,
        help_text="Número de días consecutivos de descanso para la rotación personalizada."
    )

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['horarios'].queryset = Horario.objects.filter(empresa=empresa)
            self.fields['horarios'].label_from_instance = self.horario_label

    def horario_label(self, obj):
        return f"{obj.id} - {obj.nombre} ({obj.hora_entrada.strftime('%H:%M')} - {obj.hora_salida.strftime('%H:%M')})"

    def clean(self):
        cleaned_data = super().clean()
        tipo_rotacion = cleaned_data.get('tipo_rotacion')
        horarios = cleaned_data.get('horarios')
        dias_trabajo = cleaned_data.get('dias_trabajo')
        dias_descanso = cleaned_data.get('dias_descanso')

        if not horarios:
            raise forms.ValidationError("Debe seleccionar al menos un horario.")
        if tipo_rotacion == 'personalizado':
            if not dias_trabajo or not dias_descanso:
                raise forms.ValidationError("Para rotación personalizada, debe ingresar los días de trabajo y descanso.")
            if dias_trabajo < 1 or dias_descanso < 1:
                raise forms.ValidationError("Los días de trabajo y descanso deben ser al menos 1.")
        return cleaned_data








class RegistroEntradaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['metodo', 'firma_digital']
        
    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')
        
        if metodo == 'geo':
            lat = self.data.get('latitud')
            lon = self.data.get('longitud')
            
            if not lat or not lon:
                raise forms.ValidationError("Debe habilitar la geolocalización")
                
            # Validar precisión mínima
            precision = float(self.data.get('precision', 100))
            if precision > 100:  # 50 metros máximo de error
                raise forms.ValidationError("Precisión de ubicación insuficiente")
            
class RegistroSalidaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['metodo']

