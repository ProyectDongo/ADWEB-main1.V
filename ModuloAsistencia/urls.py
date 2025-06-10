from django.urls import path
from . import views


urlpatterns = [
path('usuarios/<int:vigencia_plan_id>/crear/', views.UserCreateUpdateView.as_view(), name='create_user'),
    path('usuarios/<int:vigencia_plan_id>/editar/<int:user_id>/', views.UserCreateUpdateView.as_view(), name='update_user'),
    path('get_form_template/<str:action>/', views.GetFormTemplateView.as_view(), name='get_form_template'),
    path('usuarios/validate/', views.ValidationView.as_view(), name='validation'),
    path('validar-campo/', views.ValidationView.as_view(), name='validate_field'),
    path('validar-rut/', views.ValidationView.as_view(), name='validate_rut'),
    path('validar-email/', views.ValidationView.as_view(), name='validate_email'),
    path('delete_user/<int:vigencia_plan_id>/<int:user_id>/', views.UserCreateUpdateView.as_view(), name='delete_user'),
    path('horarios/', views.HorarioListView.as_view(), name='horarios_list'),
    path('horarios/nuevo/', views.HorarioCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/editar/', views.HorarioUpdateView.as_view(), name='horario_update'),
    path('horarios/<int:pk>/eliminar/', views.HorarioDeleteView.as_view(), name='horario_delete'),
    path('turnos/', views.TurnoListView.as_view(), name='turnos_list'),
    path('turnos/nuevo/', views.TurnoCreateView.as_view(), name='turno_create'),
    path('turnos/<int:pk>/editar/', views.TurnoUpdateView.as_view(), name='turno_update'),
    path('turnos/<int:pk>/eliminar/', views.TurnoDeleteView.as_view(), name='turno_delete'),
    path('notificaciones_supervisor_json/<int:vigencia_plan_id>/', views.notificaciones_supervisor_json, name='notificaciones_supervisor_json'),
    path('set_ubicacion_nombre/<int:vigencia_plan_id>/<str:ip_address>/', views.set_ubicacion_nombre, name='set_ubicacion_nombre'),
    path('vigencia/<int:vigencia_plan_id>/registros/', views.registros_entrada_vigencia, name='registros_entrada_vigencia'),
    path('user/<int:user_id>/full-info/', views.user_full_info, name='user_full_info'),
    path('exportar_pestanas/<int:user_id>/', views.export_selected_tabs, name='export_selected_tabs'), 
    path('supervisor/mapa/<int:vigencia_plan_id>/', views.ver_mapa_registros, name='ver_mapa_registros'),   
    path('usuario/<int:user_id>/calendario/', views.CalendarioTurnoView.as_view(), name='calendario_turno'),
    path('usuario/<int:user_id>/actualizar_dia/', views.ActualizarDiaView.as_view(), name='actualizar_dia'),
    path('supervisor/asistencia/<int:empresa_id>/<int:vigencia_plan_id>/', views.supervisor_home_asistencia, name='supervisor_home_asistencia'),

       ]