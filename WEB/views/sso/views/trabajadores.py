from django.db.models import Sum, F
from datetime import timedelta, datetime
from WEB.models import RegistroEntrada, RegistroEmpresas, Usuario
from WEB.forms import RegistroEntradaForm
from django.contrib.auth.decorators import login_required       
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone


#maneja las entradas 
def handle_entrada(request):
    context = {
        'form_entrada': RegistroEntradaForm(),
        'ultima_entrada_activa': RegistroEntrada.objects.filter(
            trabajador=request.user,
            hora_salida__isnull=True
        ).order_by('-hora_entrada').first(),
        'ultima_entrada': RegistroEntrada.objects.filter(trabajador=request.user).last()
    }
    
    if request.user.empresa is None:
        messages.error(request, "No tienes una empresa asociada. Contacta al administrador.")
        return redirect('trabajador_home')
    
    # Validación de entrada activa existente
    if RegistroEntrada.objects.filter(trabajador=request.user, hora_salida__isnull=True).exists():
        messages.error(request, 'Debes registrar la salida de tu entrada anterior antes de una nueva entrada')
        return redirect('trabajador_home')
    
    hoy = timezone.now().date()
    entradas_hoy = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_entrada__date=hoy
    ).count()
   
    if entradas_hoy >= 3:
        messages.error(request, 'Máximo 3 entradas diarias alcanzado')
        return redirect('trabajador_home')
    
    entrada = RegistroEntrada(trabajador=request.user, empresa=request.user.empresa)
    form = RegistroEntradaForm(request.POST, request.FILES, instance=entrada)
    
    if form.is_valid():
        entrada = form.save(commit=False)
        entrada.trabajador = request.user
        entrada.empresa = request.user.empresa
        
        if form.cleaned_data['metodo'] == 'geo':
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')
            if latitud and longitud:
                entrada.latitud = latitud
                entrada.longitud = longitud
            else:
                messages.error(request, 'Geolocalización requerida')
                context['form_entrada'] = form
                return render(request, 'home/users/trabajador_home.html', context)
        
        entrada.save()
        messages.success(request, 'Entrada registrada correctamente')
        return redirect('trabajador_home')
    
    messages.error(request, 'Error en el formulario')
    context['form_entrada'] = form
    return render(request, 'home/users/trabajador_home.html', context)

#----------------------------------------------------------------------- #FIN DE MANEJO DE ENTRADAS

# Manejo de salidas
def handle_salida(request):
    entrada_activa = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_salida__isnull=True
    ).order_by('-hora_entrada').first()
    
    if not entrada_activa:
        messages.error(request, 'No hay entrada activa')
        return redirect('trabajador_home')
    
    try:
        entrada_activa.hora_salida = timezone.now()
        entrada_activa.save()
        messages.success(request, f'Salida registrada a las {entrada_activa.hora_salida.strftime("%H:%M")}')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return HttpResponseRedirect(reverse('trabajador_home'))

#----------------------------------------------------------------------- #FIN DE MANEJO DE SALIDAS
# Vista principal del trabajador

@login_required
def trabajador_home(request):
    context = {
        'form_entrada': RegistroEntradaForm(),
        'ultima_entrada_activa': RegistroEntrada.objects.filter(
            trabajador=request.user,
            hora_salida__isnull=True
        ).order_by('-hora_entrada').first(),
        'ultima_entrada': RegistroEntrada.objects.filter(trabajador=request.user).last()
    }
    
    if request.method == 'POST':
        if 'entrada' in request.POST:
            return handle_entrada(request)
        if 'salida' in request.POST:
            return handle_salida(request)
    
    return render(request, 'home/users/trabajador_home.html', context)


# Funciones auxiliares
def puede_registrar_entrada(user):
    return not RegistroEntrada.objects.filter(
        trabajador=user,
        hora_salida__isnull=True
    ).exists()
def get_entrada_activa(user):
    return RegistroEntrada.objects.filter(
        trabajador=user,
        hora_salida__isnull=True
    ).order_by('-hora_entrada').first()



# Vista para ver registros de entrada y salida
@login_required
def ver_registros(request):
    def formatear_duracion(td):
        if td is None:
            return "00:00:00"
        total_segundos = td.total_seconds()
        horas = int(total_segundos // 3600)
        minutos = int((total_segundos % 3600) // 60)
        segundos = int(total_segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    registros = RegistroEntrada.objects.filter(
        trabajador=request.user
    ).order_by('-hora_entrada')
    
    hoy = timezone.now().date()
    
    # Manejo de fecha seleccionada
    fecha_seleccionada = hoy
    if 'fecha' in request.GET:
        try:
            fecha_seleccionada = datetime.strptime(
                request.GET['fecha'], '%Y-%m-%d'
            ).date()
        except ValueError:
            pass

    # Registros filtrados
    registros_filtrados = registros.filter(
        hora_entrada__date=fecha_seleccionada
    )
    
    # Calcular duraciones para cada registro
    for registro in registros_filtrados:
        if registro.hora_salida:
            delta = registro.hora_salida - registro.hora_entrada
            registro.duracion = formatear_duracion(delta)
        else:
            registro.duracion = '-'

    # Funciones agregadas
    def calcular_totales(queryset):
        resultado = queryset.aggregate(
            total=Sum(F('hora_salida') - F('hora_entrada'))
        )['total']
        return formatear_duracion(resultado)

    # Totales
    total_diario = calcular_totales(registros.filter(
        hora_entrada__date=hoy,
        hora_salida__isnull=False
    ))
    
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    total_semanal = calcular_totales(registros.filter(
        hora_entrada__date__gte=inicio_semana,
        hora_salida__isnull=False
    ))
    
    inicio_mes = hoy.replace(day=1)
    total_mensual = calcular_totales(registros.filter(
        hora_entrada__date__gte=inicio_mes,
        hora_salida__isnull=False
    ))

    context = {
        'registros': registros_filtrados,
        'total_diario': total_diario,
        'total_semanal': total_semanal,
        'total_mensual': total_mensual,
        'fecha_seleccionada': fecha_seleccionada,
        'hoy': hoy,
    }
    return render(request, 'home/users/ver_registros.html', context)

#------------------------------------------------------------------------------- #FIN DE MANEJO DE REGISTROS

