from WEB.models import *
from WEB.forms import *
from WEB.decorators import permiso_requerido
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_POST


@login_required
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
    return render(request, 'side_menu/clientes/planes/crear/crear_plan.html', {'form': form})

def listar_planes(request):
    """
    Lista todos los planes registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de planes
    """
    planes = Plan.objects.all()
    return render(request, 'side_menu/clientes/planes/lista/listar_planes.html', {'planes': planes})
