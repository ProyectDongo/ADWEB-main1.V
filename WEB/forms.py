from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Usuario, RegistroEmpresas, RegistroPermisos


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
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2', 'empresa', 'permisos']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'supervisor'
        if commit:
            user.save()
            self.save_m2m()  # Guarda los permisos (relación ManyToMany)
        return user
    
#forms para los registros de usuarios trabajador
class TrabajadorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2', 'empresa', 'permisos']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'trabajador'
        if commit:
            user.save()
            self.save_m2m()
        return user
    
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
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        super(SupervisorEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permisos'].initial = self.instance.permisos.all()

#forms para editar usuarios
class TrabajadorEditForm(UserChangeForm):
    empresa = forms.ModelChoiceField(queryset=RegistroEmpresas.objects.all(), required=False)
    permisos = forms.ModelMultipleChoiceField(
        queryset=RegistroPermisos.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'permisos']

    def __init__(self, *args, **kwargs):
        super(TrabajadorEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['permisos'].initial = self.instance.permisos.all()