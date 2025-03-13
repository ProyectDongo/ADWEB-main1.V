from WEB.models import *
from WEB.forms import *
from WEB.views.scripts import *
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_POST

# Vistas de planes
@login_required
@permiso_requerido("WEB.crear_plan")
def crear_plan(request):
    """
    Vista para crear un nuevo plan.
    
    :param request: HttpRequest
    :return: Renderizado de template con formulario de creación de plan
    """
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan creado exitosamente.')
            return redirect('listar_planes')
    else:
        form = PlanForm()
    return render(request, 'admin/clientes/planes/crear/crear_plan.html', {'form': form})

@login_required
@permiso_requerido("WEB.vista_planes")
def listar_planes(request):
    """
    Lista todos los planes registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de planes
    """
    planes = Plan.objects.all()
    return render(request, 'admin/clientes/planes/lista/listar_planes.html', {'planes': planes})
