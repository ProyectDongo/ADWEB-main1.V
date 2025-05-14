
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

