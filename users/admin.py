from django.contrib import admin
from users.models import Usuario
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    # Estos campos aparecerán en la lista de usuarios
    list_display = ('username', 'rut', 'email', 'role', 'is_locked', 'is_staff')
    list_filter = ('role', 'is_locked', 'is_staff', 'is_superuser')

    # Agrupa y ordena los campos del detalle de usuario
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('rut', 'email', 'celular')}),
        ('Permisos', {
            'fields': (
                'is_active', 'is_locked', 'role',
                'groups', 'user_permissions'
            )
        }),
        ('Empresa y plan', {'fields': ('empresa', 'vigencia_plan')}),
        ('Horario y turno', {'fields': ('horario', 'turno')}),
        ('Registro permitido', {'fields': ('metodo_registro_permitido',)}),
        ('Fechas importantes', {'fields': ('last_login', 'last_failed_login')}),
    )

    # Añade los campos que quieres que aparezcan al crear un usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'rut', 'email',
                'password1', 'password2', 'role',
                'empresa', 'vigencia_plan'
            ),
        }),
    )

    search_fields = ('username', 'rut', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)
