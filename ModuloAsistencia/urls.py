from django.urls import path
from ModuloAsistencia.views import trabajadores,supervisores


urlpatterns = [
    path('usuarios/<int:vigencia_plan_id>/crear/', supervisores.UserCreateUpdateView.as_view(), name='create_user'),
    path('usuarios/<int:vigencia_plan_id>/editar/<int:user_id>/', supervisores.UserCreateUpdateView.as_view(), name='update_user'),
    path('get_form_template/<str:action>/', supervisores.GetFormTemplateView.as_view(), name='get_form_template'),
    path('usuarios/validate/', supervisores.ValidationView.as_view(), name='validation'),
    path('validar-campo/', supervisores.ValidationView.as_view(), name='validate_field'),
    path('validar-rut/', supervisores.ValidationView.as_view(), name='validate_rut'),
    path('validar-email/', supervisores.ValidationView.as_view(), name='validate_email'),
    path('delete_user/<int:vigencia_plan_id>/<int:user_id>/', supervisores.UserCreateUpdateView.as_view(), name='delete_user'),
    path('horarios/', supervisores.HorarioListView.as_view(), name='horarios_list'),
    path('horarios/nuevo/', supervisores.HorarioCreateView.as_view(), name='horario_create'),
    path('horarios/<int:pk>/editar/', supervisores.HorarioUpdateView.as_view(), name='horario_update'),
    path('horarios/<int:pk>/eliminar/', supervisores.HorarioDeleteView.as_view(), name='horario_delete'),
    path('turnos/', supervisores.TurnoListView.as_view(), name='turnos_list'),
    path('turnos/nuevo/', supervisores.TurnoCreateView.as_view(), name='turno_create'),
    path('turnos/<int:pk>/editar/', supervisores.TurnoUpdateView.as_view(), name='turno_update'),
    path('turnos/<int:pk>/eliminar/', supervisores.TurnoDeleteView.as_view(), name='turno_delete'),
    path('notificaciones_supervisor_json/<int:vigencia_plan_id>/', supervisores.notificaciones_supervisor_json, name='notificaciones_supervisor_json'),
    path('set_ubicacion_nombre/<int:vigencia_plan_id>/<str:ip_address>/', supervisores.set_ubicacion_nombre, name='set_ubicacion_nombre'),
    path('vigencia/<int:vigencia_plan_id>/registros/', supervisores.registros_entrada_vigencia, name='registros_entrada_vigencia'),
    path('user/<int:user_id>/full-info/', supervisores.user_full_info, name='user_full_info'),
    path('exportar_pestanas/<int:user_id>/', supervisores.export_selected_tabs, name='export_selected_tabs'), 
    path('supervisor/mapa/<int:vigencia_plan_id>/', supervisores.ver_mapa_registros, name='ver_mapa_registros'),   
    path('usuario/<int:user_id>/calendario/', supervisores.CalendarioTurnoView.as_view(), name='calendario_turno'),
    path('usuario/<int:user_id>/actualizar_dia/', supervisores.ActualizarDiaView.as_view(), name='actualizar_dia'),
    path('supervisor/asistencia/<int:empresa_id>/<int:vigencia_plan_id>/', supervisores.supervisor_home_asistencia, name='supervisor_home_asistencia'),
    path('generar-asignaciones/<int:user_id>/', supervisores.GenerarAsignacionesView.as_view(), name='generar_asignaciones'),
    path('late_arrival_notifications_json/<int:vigencia_plan_id>/', supervisores.late_arrival_notifications_json, name='late_arrival_notifications_json'),
    path('send_access_code/<int:notification_id>/', supervisores.send_access_code, name='send_access_code'),
    path('late_arrival_history/<int:vigencia_plan_id>/', supervisores.late_arrival_history, name='late_arrival_history'),

    #registro de supervisores 
    path('supervisor/selector/', supervisores.SupervisorSelectorView.as_view(), name='supervisor_selector'),
    path('supervisor/register/<int:empresa_id>/<int:vigencia_plan_id>/', supervisores.supervisor_register, name='supervisor_register'),

    # URL para la vista de los Trabajadores de la empresa
    path('trabajador_home/', trabajadores.trabajador_home, name='trabajador_home'),
    path('ver_registros/', trabajadores.ver_registros, name='ver_registros'),


       ]