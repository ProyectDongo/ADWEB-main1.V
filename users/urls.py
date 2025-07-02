from django.urls import path 
from django_ratelimit.decorators import ratelimit
from users import views 

urlpatterns = [

    path('login/', ratelimit(key='post:username', method='POST', rate='5/h')(views.LoginUnificado.as_view()), name='login'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('generar-reporte/', views.generar_reporte, name='generar_reporte'),
    path('supervisor/selector/<int:empresa_id>/', views.supervisor_selector_modulo, name='supervisor_selector_modulo'),
    path('configuracion_home/', views.configuracion_home, name='configuracion_home'),

   ]