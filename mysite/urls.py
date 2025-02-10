"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib.auth import views as auth_views
from django.urls import path
from WEB import views

urlpatterns = [
    # Ruta para el login
    path('', auth_views.LoginView.as_view(template_name='login/login.html', redirect_authenticated_user=True), name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Ruta para el logout
    path('accounts/logout/', views.logout_view, name='logout'),
    # Ruta para la redirección después del login
    path('accounts/redirect/', views.redirect_after_login, name='redirect_after_login'),
    # Rutas para las páginas de inicio de admin, supervisor y trabajador
    path('admin/home/', views.admin_home, name='admin_home'),
    path('supervisor/home/', views.supervisor_home, name='supervisor_home'),
    path('trabajador/home/', views.trabajador_home, name='trabajador_home'),

    # Rutas para crear empresas, permisos, admins, supervisores y trabajadores
    path('crear_empresa/', views.crear_empresa, name='crear_empresa'),
    path('crear_permiso/', views.crear_permiso, name='crear_permiso'),
    path('crear_admin/', views.crear_admin, name='crear_admin'),
    path('crear_supervisor/', views.crear_supervisor, name='crear_supervisor'),
    path('crear_trabajador/', views.crear_trabajador, name='crear_trabajador'),

    #lista permisos
    path('lista_permisos/', views.lista_permisos, name='lista_permisos'),
    
 
   
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

   

    # habilitar otra entrada
    path('habilitar_otra_entrada/<int:entrada_id>/', views.habilitar_otra_entrada, name='habilitar_otra_entrada'),
    # estas 2 son de la misma funcion
    path('actualizar_limites/<int:empresa_id>/', views.actualizar_limites, name='actualizar_limites'),
    path('listar_empresas/', views.listar_empresas, name='listar_empresas'),
    
    path('editar_supervisor/<int:pk>/', views.editar_supervisor, name='editar_supervisor'),
    path('editar_trabajador/<int:pk>/', views.editar_trabajador, name='editar_trabajador'),

    # Rutas para las entradas para la empresa
    path('vigencia_planes/', views.vigencia_planes, name='vigencia_planes'),
    
    # Rutas para las entradas para la empresa
    path('api/get_provincias/', views.get_provincias, name='get_provincias'),
    path('api/get_comunas/', views.get_comunas, name='get_comunas'),
    
    path('empresa_form/', views.editar_empresa, name='empresa_form'),
   # Editar y eliminar empresa
    path('editar_empresa/<int:pk>/', views.editar_empresa, name='editar_empresa'),
    path('eliminar_empresa/<int:pk>/', views.eliminar_empresa, name='eliminar_empresa'),
    path('detalle_empresa/<int:pk>/', views.detalle_empresa, name='detalle_empresa'),
    path('empresas_vigentes/', views.empresas_vigentes, name='empresas_vigentes'),
    path('listar_planes/', views.listar_planes, name='listar_planes'),
    path('generar_boleta/<int:empresa_id>/', views.generar_boleta, name='generar_boleta'),
    # Rutas para los planes
    path('crear_plan/', views.crear_plan, name='crear_plan'), 

    # ruta configuracion
    path('configuracion_home/', views.configuracion_home, name='configuracion_home'),
    
    path('vigencia_planes/<int:pk>/', views.vigencia_planes, name='vigencia_planes'),
    
    
    
    ] 