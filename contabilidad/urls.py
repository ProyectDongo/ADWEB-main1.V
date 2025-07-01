from django.urls import path 
from contabilidad import views 

urlpatterns = [


    path('supervisor/contabilidad/<int:empresa_id>/<int:vigencia_plan_id>/', views.supervisor_home_contabilidad, name='supervisor_home_contabilidad'),
   ]