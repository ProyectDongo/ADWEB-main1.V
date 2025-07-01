from django.urls import path 
from geografia import views

urlpatterns = [
path('api/get_provincias/', views.get_provincias, name='get_provincias'),
path('api/get_comunas/', views.get_comunas, name='get_comunas'),
  ]