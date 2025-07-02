from django.urls import path 
from . import views 

urlpatterns = [


    path('supervisor/almacen/<int:empresa_id>/<int:vigencia_plan_id>/', views.supervisor_home_almacen, name='supervisor_home_almacen'),
   ]