
from django.urls import path, include
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

from WEB.views.admin.GestionPlanes.views import gestion_planes
from WEB.views.admin.config.views import sofware
from WEB.views.admin.estadisticas.views import estadisticas
from WEB.views.admin.clientes.empresa.views import empresas, planes




urlpatterns = [
    # ------------------------------------------------------------------------------------ #
    # Superusuario y Administración
    # ------------------------------------------------------------------------------------ #
    path('django-admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # ------------------------------------------------------------------------------------ #
    # Autenticación y Selección de Roles
    path('users/', include('users.urls')),

    # ------------------------------------------------------------------------------------ #

    path('', RedirectView.as_view(url='/users/login/', permanent=True)),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # ------------------------------------------------------------------------------------ #
    # Homes según Rol
    # ------------------------------------------------------------------------------------ #

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


      # Pagos
    # ------------------------------------------------------------------------------------ #
    path('transacciones/', include('transacciones.urls')),

    # ------------------------------------------------------------------------------------ #
        # inventario
    path('ModuloInventario/',include('ModuloInventario.urls')),
    # ------------------------------------------------------------------------------------ #
        # contabilidad
    path('ModuloContabilidad/',include('ModuloContabilidad.urls')),
    # ------------------------------------------------------------------------------------ #
    

    # ------------------------------------------------------------------------------------ #
    # Utilidades y APIs
    # ------------------------------------------------------------------------------------ #
    path('geografia/', include('geografia.urls')),
   
    # ------------------------------------------------------------------------------------ #
    path('biometrics/', include('biometrics.urls')),
    path('ModuloAsistencia/', include('ModuloAsistencia.urls')),

    # ------------------------------------------------------------------------------------ #
    # Otras URL
    # ------------------------------------------------------------------------------------ #
]