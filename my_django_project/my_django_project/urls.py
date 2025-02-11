from django.urls import path
from my_app.views import editar_vigencia_plan

urlpatterns = [
    path('editar_vigencia_plan/<int:id>/', editar_vigencia_plan, name='editar_vigencia_plan'),
]