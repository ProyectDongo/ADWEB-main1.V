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

    #lista empresas
    path('lista_empresas/', views.lista_empresas, name='lista_empresas'),
    path('lista_permisos/', views.lista_permisos, name='lista_permisos'),
    
    #lista permisos
    path('detalles_empresa/<int:empresa_id>/', views.detalles_empresa, name='detalles_empresa'),
    path('editar_supervisor/<int:user_id>/', views.editar_supervisor, name='editar_supervisor'),
    path('editar_trabajador/<int:user_id>/', views.editar_trabajador, name='editar_trabajador'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Editar y eliminar empresa
    path('editar_empresa/<int:empresa_id>/', views.editar_empresa, name='editar_empresa'),
    path('eliminar_empresa/<int:empresa_id>/', views.eliminar_empresa, name='eliminar_empresa'),

]