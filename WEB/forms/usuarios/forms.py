import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from WEB.models.usuarios.usuario import Usuario
from WEB.models.empresa.empresa import RegistroEmpresas
from WEB.views.scripts import *

class AdminForm(UserCreationForm):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label="Grupos de Permisos"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2', 'grupos']
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
            user.groups.set(self.cleaned_data['grupos'])
        return user

class SupervisorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_grupos'}),
        required=False,
        label="Grupos de Permisos"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'nombre', 'last_name', 'apellidoM', 'celular', 'email', 'password1', 'password2', 'empresa', 'grupos']
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
            self.fields['grupos'].queryset = user.groups.all()
        elif user and user.role == 'admin':
            self.fields['grupos'].queryset = Group.objects.all()

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)
        return format_rut(rut)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.role = 'supervisor'
        if commit:
            usuario.save()
            usuario.groups.set(self.cleaned_data['grupos'])
        return usuario

class TrabajadorForm(UserCreationForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_grupos'}),
        required=False,
        label="Grupos de Permisos"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'rut', 'nombre', 'last_name', 'apellidoM', 'celular', 'email', 'password1', 'password2', 'empresa', 'grupos']
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
            self.fields['grupos'].queryset = user.groups.all()
        elif user and user.role == 'admin':
            self.fields['grupos'].queryset = Group.objects.all()

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)
        return format_rut(rut)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'trabajador'
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['grupos'])
        return user

class AdminEditForm(UserChangeForm):
    empresa = forms.ModelChoiceField(
        queryset=RegistroEmpresas.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grupos de Permisos"
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'empresa', 'grupos']

class SupervisorEditForm(UserChangeForm):
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

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

