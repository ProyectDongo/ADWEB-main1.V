
from django.urls import include, path
from transacciones import views

urlpatterns = [
    path('empresa/<int:empresa_id>/pagos/', views.gestion_pagos, name='gestion_pagos'),
    path('pago/actualizar/<int:pago_id>/', views.actualizar_estado_pago, name='actualizar_estado_pago'),
    path('notificaciones/json/', views.notificaciones_json, name='notificaciones_json'),
    path('empresa/<int:empresa_id>/cobros/registrar/', views.registrar_cobro, name='registrar_cobro'),
    path('empresa/<int:empresa_id>/cobro/<int:cobro_id>/actualizar/', views.actualizar_cobro, name='actualizar_cobro'),
    path('enviar-notificacion/<int:empresa_id>/', views.enviar_notificacion, name='enviar_notificacion'),
       ]