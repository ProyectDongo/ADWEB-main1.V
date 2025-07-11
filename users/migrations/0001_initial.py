# Generated by Django 5.1.7 on 2025-07-02 16:08

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import users.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WEB', '__first__'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('rut', models.CharField(max_length=12, unique=True, validators=[users.validators.validar_rut])),
                ('role', models.CharField(choices=[('admin', 'Administrador'), ('supervisor', 'Supervisor'), ('trabajador', 'Trabajador')], default='admin', max_length=20)),
                ('celular', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('is_locked', models.BooleanField(default=False, help_text='Indica si la cuenta está bloqueada por seguridad', verbose_name='Cuenta bloqueada')),
                ('failed_login_attempts', models.PositiveIntegerField(default=0, verbose_name='Intentos fallidos')),
                ('last_failed_login', models.DateTimeField(blank=True, null=True, verbose_name='Último intento fallido')),
                ('metodo_registro_permitido', models.CharField(choices=[('firma', 'Firma Digital'), ('huella', 'Huella Digital'), ('geo', 'Geolocalización')], default='firma', max_length=20)),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='WEB.registroempresas')),
                ('groups', models.ManyToManyField(blank=True, help_text='Grupos a los que pertenece el usuario', related_name='usuarios', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Permisos específicos para este usuario', related_name='usuarios', to='auth.permission', verbose_name='user permissions')),
                ('vigencia_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='WEB.vigenciaplan')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
                'permissions': [('eliminar_trabajador', 'Permiso para eliminar trabajadores'), ('eliminar_supervisor', 'Permiso para eliminar supervisores'), ('eliminar_admin', 'Permiso para eliminar administradores'), ('crear_admin', 'Permiso para crear administradores'), ('crear_supervisor', 'Permiso para crear supervisores'), ('crear_trabajador', 'Permiso para crear trabajadores'), ('editar_supervisor', 'permiso para editar supervisores'), ('editar_trabajador', 'permiso para editar trabajadores')],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ContactoUsuario',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('direccion', models.CharField(blank=True, max_length=255, null=True)),
                ('numero', models.CharField(blank=True, max_length=10, null=True)),
                ('dpto', models.CharField(blank=True, max_length=10, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('celular', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('provincia', models.CharField(blank=True, max_length=100, null=True)),
                ('comuna', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InformacionAdicional',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('fecha_primera_cotizacion', models.DateField(blank=True, null=True)),
                ('anos_anteriores', models.IntegerField(blank=True, null=True)),
                ('meses_anteriores', models.IntegerField(blank=True, null=True)),
                ('dias_vacaciones_usados', models.IntegerField(blank=True, null=True)),
                ('fecha_reconocimiento_vacaciones', models.DateField(blank=True, null=True)),
                ('dias_vacaciones_anuales', models.IntegerField(blank=True, null=True)),
                ('ajustes_vacaciones_progresivas', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InformacionBancaria',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('banco', models.CharField(blank=True, choices=[('banco_estado', 'Banco Estado'), ('banco_chile', 'Banco de Chile'), ('santander', 'Santander'), ('bci', 'BCI'), ('itau', 'Itaú'), ('scotiabank', 'Scotiabank'), ('falabella', 'Banco Falabella')], max_length=50, null=True)),
                ('tipo_cuenta', models.CharField(blank=True, choices=[('vista', 'Cuenta Vista'), ('corriente', 'Cuenta Corriente'), ('ahorro', 'Cuenta de Ahorro')], max_length=50, null=True)),
                ('numero_cuenta', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InformacionComplementaria',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('pais_origen', models.CharField(blank=True, max_length=100, null=True)),
                ('pasaporte', models.CharField(blank=True, max_length=50, null=True)),
                ('estado_civil', models.CharField(blank=True, max_length=50, null=True)),
                ('tipo_visa', models.CharField(blank=True, max_length=50, null=True)),
                ('numero_calzado', models.CharField(blank=True, max_length=10, null=True)),
                ('talla_ropa', models.CharField(blank=True, max_length=10, null=True)),
                ('grupo_sanguineo', models.CharField(blank=True, max_length=10, null=True)),
                ('alergico', models.TextField(blank=True, null=True)),
                ('personal_destacado', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Otros',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('tipo_discapacidad', models.CharField(blank=True, max_length=100, null=True)),
                ('tasa_indemnizacion', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('apellido_paterno', models.CharField(blank=True, max_length=100, null=True)),
                ('apellido_materno', models.CharField(blank=True, max_length=100, null=True)),
                ('nombres', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('edad', models.IntegerField(blank=True, null=True)),
                ('nacionalidad', models.CharField(blank=True, max_length=100, null=True)),
                ('sexo', models.CharField(blank=True, max_length=10, null=True)),
                ('fecha_contrato', models.DateField(blank=True, null=True)),
                ('fecha_termino', models.DateField(blank=True, null=True)),
                ('cargo', models.CharField(blank=True, max_length=100, null=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('sindicato', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_ingreso_sindicato', models.DateField(blank=True, null=True)),
                ('tipo_jornada', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Prevision',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('salud', models.CharField(blank=True, choices=[('fonasa', 'Fonasa'), ('isapre', 'Isapre')], max_length=100, null=True)),
                ('regimen', models.CharField(blank=True, choices=[('actual', 'Régimen Actual'), ('antiguo', 'Régimen Antiguo (IPS)')], max_length=50, null=True)),
                ('tasa', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('afp', models.CharField(blank=True, choices=[('capital', 'Capital'), ('cuprum', 'Cuprum'), ('habitat', 'Habitat'), ('modelo', 'Modelo'), ('planvital', 'Planvital'), ('provida', 'Provida'), ('uno', 'Uno')], max_length=100, null=True)),
                ('pensionado', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SeguroCesantia',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('acogido_seguro', models.BooleanField(default=False)),
                ('afp_recaudadora', models.CharField(blank=True, max_length=100, null=True)),
                ('sueldo_patronal', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('acogido_seguro_accidentes', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AccessCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AntecedentesConducir',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_licencia', models.CharField(blank=True, max_length=50, null=True)),
                ('municipalidad', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_ultimo_control', models.DateField(blank=True, null=True)),
                ('fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('hoja_vida_conducir', models.TextField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='antecedentes_conducir', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AuditoriaAcceso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('exito', models.BooleanField(default=False)),
                ('motivo', models.TextField(blank=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Capacitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('horas', models.IntegerField(blank=True, null=True)),
                ('institucion', models.CharField(blank=True, max_length=100, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='capacitaciones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExamenesMutual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_examen', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_examen', models.DateField(blank=True, null=True)),
                ('fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examenes_mutual', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GrupoFamiliar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut_carga', models.CharField(blank=True, max_length=12, null=True, validators=[users.validators.validar_rut])),
                ('nombre_carga', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('edad', models.IntegerField(blank=True, null=True)),
                ('sexo', models.CharField(blank=True, choices=[('MASCULINO', 'masculino'), ('FEMENINO', 'femenino')], max_length=10, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grupo_familiar', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('hora_entrada', models.TimeField()),
                ('hora_salida', models.TimeField()),
                ('tolerancia_retraso', models.IntegerField(default=20, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(60)])),
                ('tolerancia_horas_extra', models.IntegerField(default=20, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(60)])),
                ('tipo_horario', models.CharField(choices=[('diurno', 'Diurno'), ('nocturno', 'Nocturno'), ('mixto', 'Mixto')], default='diurno', max_length=20)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='WEB.registroempresas')),
            ],
        ),
        migrations.AddField(
            model_name='usuario',
            name='horario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios', to='users.horario'),
        ),
        migrations.CreateModel(
            name='LateArrivalNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('code_sent', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LicenciasMedicas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_accidente', models.CharField(blank=True, max_length=100, null=True)),
                ('clasificacion_accidente', models.CharField(blank=True, max_length=100, null=True)),
                ('fecha_inicio_reposo', models.DateField(blank=True, null=True)),
                ('fecha_termino', models.DateField(blank=True, null=True)),
                ('fecha_alta', models.DateField(blank=True, null=True)),
                ('dias_reposo', models.IntegerField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licencias_medicas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NivelEstudios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel_estudios', models.CharField(blank=True, max_length=100, null=True)),
                ('completo', models.BooleanField(default=False)),
                ('ultimo_curso', models.CharField(blank=True, max_length=100, null=True)),
                ('carrera', models.CharField(blank=True, max_length=100, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='niveles_estudios', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('dias_trabajo', models.IntegerField(blank=True, null=True)),
                ('dias_descanso', models.IntegerField(blank=True, null=True)),
                ('inicio_turno', models.DateField(blank=True, null=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turnos', to='WEB.registroempresas')),
            ],
        ),
        migrations.AddField(
            model_name='usuario',
            name='turno',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios', to='users.turno'),
        ),
        migrations.CreateModel(
            name='DiaHabilitado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('habilitado', models.BooleanField(default=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dias_habilitados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('usuario', 'fecha')},
            },
        ),
        migrations.CreateModel(
            name='AsignacionDiaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones_diarias', to=settings.AUTH_USER_MODEL)),
                ('horario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.horario')),
            ],
            options={
                'unique_together': {('usuario', 'fecha')},
            },
        ),
    ]
