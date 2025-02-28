
from django.http import JsonResponse
from WEB.forms import *
from WEB.models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from django.contrib.auth.decorators import login_required


def get_comunas(request):
    """
    Obtiene las comunas de una provincia específica en formato JSON.
    
    :param request: HttpRequest con parámetro GET 'provincia_id'
    :return: JsonResponse con lista de comunas o mensaje de error
    :rtype: JsonResponse
    """
    provincia_id = request.GET.get('provincia_id')
    if provincia_id:
        comunas = Comuna.objects.filter(provincia_id=provincia_id).values('id', 'nombre')
        return JsonResponse(list(comunas), safe=False)
    return JsonResponse({'error': 'No provincia_id provided'}, status=400)

def get_provincias(request):
    """
    Obtiene las provincias de una región específica en formato JSON.
    
    :param request: HttpRequest con parámetro GET 'region_id'
    :return: JsonResponse con lista de provincias o mensaje de error
    :rtype: JsonResponse
    """
    region_id = request.GET.get('region_id')
    if region_id:
        provincias = Provincia.objects.filter(region_id=region_id).values('id', 'nombre')
        return JsonResponse(list(provincias), safe=False)
    return JsonResponse({'error': 'No region_id provided'}, status=400)

def get_regiones(request):
    """
    Obtiene todas las regiones disponibles en formato JSON.
    
    :param request: HttpRequest
    :return: JsonResponse con lista de regiones
    :rtype: JsonResponse
    """
    regiones = Region.objects.all().values('id', 'nombre')
    return JsonResponse(list(regiones), safe=False)


@login_required
#@permiso_requerido("editar_vigencia")
def editar_vigencia_plan(request, plan_id):
    """
    Vista para editar la vigencia de un plan existente.

    Esta vista permite a los usuarios autenticados editar los detalles de la vigencia de un plan específico.
    Si la solicitud es un POST, se valida y guarda el formulario. Si es GET, se muestra el formulario con los
    datos actuales del plan.

    :param request: HttpRequest
    :param plan_id: ID de la vigencia del plan a editar
    :return: Renderizado del template 'empresas/editar_vigencia_plan.html' con el formulario de edición
    """
    # Obtener el objeto VigenciaPlan o devolver un 404 si no existe
    plan = get_object_or_404(VigenciaPlan, id=plan_id)
    
    if request.method == 'POST':
        # Si la solicitud es POST, crear un formulario con los datos enviados y la instancia del plan
        form = PlanVigenciaForm(request.POST, instance=plan)
        if form.is_valid():
            # Si el formulario es válido, guardar los cambios
            form.save()
            # Mostrar un mensaje de éxito
            messages.success(request, 'Plan actualizado exitosamente.')
            # Redirigir a la lista de empresas
            return redirect('listar_clientes')
    else:
        # Si la solicitud es GET, crear un formulario con la instancia del plan
        form = PlanVigenciaForm(instance=plan)
    
    # Renderizar el template con el formulario y el plan
    return render(request, 'side_menu/clientes/lista_clientes/servicios/editar/editar_vigencia_plan.html', {'form': form, 'plan': plan})
