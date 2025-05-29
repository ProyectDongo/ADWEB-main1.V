from site import venv
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django_ratelimit.decorators import ratelimit
from django.views.generic import RedirectView

from WEB.views.admin.GestionPlanes.views import gestion_planes
from WEB.views.autentificaion.views import autenticacion
from WEB.views.admin.config.views import sofware
from WEB.views.admin.estadisticas.views import estadisticas
from WEB.views.tools.views import utilidades
from WEB.views.admin.clientes.pagos.views import pagos
from WEB.views.admin.clientes.empresa.views import empresas, planes
from WEB.views.supervisor.modulos.views import almacen, asistencia, contabilidad,selector
from WEB.views.trabajador.views import trabajadores

urlpatterns = [
    # ------------------------------------------------------------------------------------ #
    # Superusuario y Administración
    # ------------------------------------------------------------------------------------ #
    path('django-admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # ------------------------------------------------------------------------------------ #
    # Autenticación y Selección de Roles
    # ------------------------------------------------------------------------------------ #
    
    path('', RedirectView.as_view(url='/login/', permanent=True)),
    path('login/', ratelimit(key='post:username', method='POST', rate='5/h')(autenticacion.LoginUnificado.as_view()), name='login'),
    path('supervisor/selector/', selector.SupervisorSelectorView.as_view(), name='supervisor_selector'),
    path('supervisor/register/', selector.supervisor_register, name='supervisor_register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('redirect-after-login/', autenticacion.redirect_after_login, name='redirect_after_login'),

    # ------------------------------------------------------------------------------------ #
    # Homes según Rol
    # ------------------------------------------------------------------------------------ #
    path('admin_home/', autenticacion.admin_home, name='admin_home'),
    path('generar-reporte/', autenticacion.generar_reporte, name='generar_reporte'),
    path('supervisor/selector/<int:empresa_id>/', autenticacion.supervisor_selector_modulo, name='supervisor_selector_modulo'),
    path('supervisor/asistencia/<int:empresa_id>/<int:vigencia_plan_id>/', asistencia.supervisor_home_asistencia, name='supervisor_home_asistencia'),
    path('supervisor/contabilidad/<int:empresa_id>/<int:vigencia_plan_id>/', contabilidad.supervisor_home_contabilidad, name='supervisor_home_contabilidad'),
    path('supervisor/almacen/<int:empresa_id>/<int:vigencia_plan_id>/', almacen.supervisor_home_almacen, name='supervisor_home_almacen'),
    path('trabajador_home/', trabajadores.trabajador_home, name='trabajador_home'),
    path('configuracion_home/', autenticacion.configuracion_home, name='configuracion_home'),

    # ------------------------------------------------------------------------------------ #
    # Software (Creación de Usuarios y Vigencias)
    # ------------------------------------------------------------------------------------ #
    path('crear_admin/', sofware.crear_admin, name='crear_admin'),
    path('crear_supervisor/', sofware.crear_supervisor, name='crear_supervisor'),
    path('crear_trabajador/', sofware.crear_trabajador, name='crear_trabajador'),
    path('api/vigencias/', sofware.get_vigencias, name='get_vigencias'),

    # ------------------------------------------------------------------------------------ #
    # Clientes y Empresas
    # ------------------------------------------------------------------------------------ #
    path('listar_clientes/', empresas.listar_clientes, name='listar_clientes'),
    path('crear_empresa/', empresas.crear_empresa, name='crear_empresa'),
    path('eliminar_empresa/<int:pk>/', empresas.eliminar_empresa, name='eliminar_empresa'),
    path('empresas/eliminadas/', empresas.listar_empresas_eliminadas, name='listar_empresas_eliminadas'),
    path('empresa/recuperar/<int:id>/', empresas.recuperar_empresa, name='recuperar_empresa'),
    path('detalle_empresa/<int:pk>/', empresas.detalle_empresa, name='detalle_empresa'),
    path('vigencia_planes/<int:pk>/', empresas.vigencia_planes, name='vigencia_planes'),
    path('check-codigo-plan/', empresas.check_codigo_plan, name='check_codigo_plan'),

    # ------------------------------------------------------------------------------------ #
    # Pagos
    # ------------------------------------------------------------------------------------ #
    path('empresa/<int:empresa_id>/pagos/', pagos.gestion_pagos, name='gestion_pagos'),
    path('pago/actualizar/<int:pago_id>/', pagos.actualizar_estado_pago, name='actualizar_estado_pago'),
    path('notificaciones/json/', pagos.notificaciones_json, name='notificaciones_json'),
    path('empresa/<int:empresa_id>/cobros/registrar/', pagos.registrar_cobro, name='registrar_cobro'),
    path('empresa/<int:empresa_id>/cobro/<int:cobro_id>/actualizar/', pagos.actualizar_cobro, name='actualizar_cobro'),
    path('enviar-notificacion/<int:empresa_id>/', pagos.enviar_notificacion, name='enviar_notificacion'),

    # ------------------------------------------------------------------------------------ #
    # Planes
    # ------------------------------------------------------------------------------------ #
    path('listar_planes/', planes.listar_planes, name='listar_planes'),
    path('crear_plan/', planes.crear_plan, name='crear_plan'),

    # ------------------------------------------------------------------------------------ #
    # Estadísticas
    # ------------------------------------------------------------------------------------ #
    path('home_estadisticas/', estadisticas.home_estadisticas, name='home_estadisticas'),  # 
    path('estadisticas/empresas/', estadisticas.estadisticas_empresas, name='estadisticas_empresas'),
    path('estadisticas/pagos/', estadisticas.estadisticas_pagos, name='estadisticas_pagos'),

    # ------------------------------------------------------------------------------------ #
    # Módulo de Asistencia
    # ------------------------------------------------------------------------------------ #
    path('validate-rut/', gestion_planes.validate_rut, name='validate_rut'),
    path('empresa/<int:pk>/', gestion_planes.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresa/<int:empresa_pk>/vigencia/<int:vigencia_pk>/supervisor/crear/', gestion_planes.SupervisorCreateView.as_view(), name='supervisor_create'),
    path('empresa/<int:empresa_pk>/vigencia/<int:vigencia_pk>/usuario/crear/', gestion_planes.UsuarioCreateVigenciaView.as_view(), name='usuario_create_vigencia'),
    path('usuario/editar/<int:pk>/', gestion_planes.UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('usuario/eliminar/<int:pk>/', gestion_planes.UsuarioDeleteView.as_view(), name='usuario_delete'),
    path('vigencia-plan/<int:pk>/edit/', gestion_planes.VigenciaPlanUpdateView.as_view(), name='vigencia_plan_edit'),
    path('vigencia/<int:pk>/cambiar-estado/', gestion_planes.VigenciaPlanStatusToggleView.as_view(), name='toggle_vigencia_status'),
    path('cuenta-bloqueada/', gestion_planes.CuentaBloqueadaView.as_view(), name='cuenta_bloqueada'),
    path('gestion-usuarios/', lambda request: redirect('empresa_detail', pk=1), name='gestion_usuarios'),
    path('gestion-planes/', lambda request: redirect('empresa_detail', pk=1), name='gestion_planes'),
    path('eliminar_huella/<int:user_id>/', gestion_planes.eliminar_huella, name='eliminar_huella'),
    path('usuario/<int:user_id>/calendario/', asistencia.CalendarioTurnoView.as_view(), name='calendario_turno'),
    path('usuario/<int:user_id>/actualizar_dia/', asistencia.ActualizarDiaView.as_view(), name='actualizar_dia'),


    # ------------------------------------------------------------------------------------ #
    # Supervisor
    # ------------------------------------------------------------------------------------ #
    path('usuarios/<int:vigencia_plan_id>/crear/', asistencia.UserCreateUpdateView.as_view(), name='create_user'),
    path('usuarios/<int:vigencia_plan_id>/editar/<int:user_id>/', asistencia.UserCreateUpdateView.as_view(), name='update_user'),
    path('get_form_template/<str:action>/', asistencia.GetFormTemplateView.as_view(), name='get_form_template'),
    path('usuarios/validate/', asistencia.ValidationView.as_view(), name='validation'),
    path('validar-campo/', asistencia.ValidationView.as_view(), name='validate_field'),
    path('validar-rut/', asistencia.ValidationView.as_view(), name='validate_rut'),
    path('validar-email/', asistencia.ValidationView.as_view(), name='validate_email'),
    path('delete_user/<int:vigencia_plan_id>/<int:user_id>/', asistencia.UserCreateUpdateView.as_view(), name='delete_user'),
    path('horarios/', asistencia.HorarioListView.as_view(), name='horarios_list'),
    path('horarios/nuevo/', asistencia.HorarioCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/editar/', asistencia.HorarioUpdateView.as_view(), name='horario_update'),
    path('horarios/<int:pk>/eliminar/', asistencia.HorarioDeleteView.as_view(), name='horario_delete'),
    path('turnos/', asistencia.TurnoListView.as_view(), name='turnos_list'),
    path('turnos/nuevo/', asistencia.TurnoCreateView.as_view(), name='turno_create'),
    path('turnos/<int:pk>/editar/', asistencia.TurnoUpdateView.as_view(), name='turno_update'),
    path('turnos/<int:pk>/eliminar/', asistencia.TurnoDeleteView.as_view(), name='turno_delete'),

    # ------------------------------------------------------------------------------------ #
    # Utilidades y APIs
    # ------------------------------------------------------------------------------------ #
    path('api/get_provincias/', utilidades.get_provincias, name='get_provincias'),
    path('api/get_comunas/', utilidades.get_comunas, name='get_comunas'),
    path('notificaciones_supervisor_json/<int:vigencia_plan_id>/', asistencia.notificaciones_supervisor_json, name='notificaciones_supervisor_json'),
    path('set_ubicacion_nombre/<int:vigencia_plan_id>/<str:ip_address>/', asistencia.set_ubicacion_nombre, name='set_ubicacion_nombre'),
    path('vigencia/<int:vigencia_plan_id>/registros/', asistencia.registros_entrada_vigencia, name='registros_entrada_vigencia'),
    # ------------------------------------------------------------------------------------ #
    # Biometría
    # ------------------------------------------------------------------------------------ #
    path('biometrics/', include('biometrics.urls')),

    # ------------------------------------------------------------------------------------ #
    # Otras URL
    # ------------------------------------------------------------------------------------ #
    path('ver_registros/', trabajadores.ver_registros, name='ver_registros'),
]