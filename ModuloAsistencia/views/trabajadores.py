from django.db.models import Sum, F
from datetime import timedelta, datetime
from WEB.models import  RegistroEmpresas, Usuario,Notificacion
from WEB.forms.modulo_asistencia.forms import *
from django.contrib.auth.decorators import login_required       
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from ModuloAsistencia.models import RegistroEntrada
import random
import string
from django.core.mail import send_mail
from ModuloAsistencia.views.supervisores import get_today_assignment,generate_access_code, send_access_code_email
import logging
from openpyxl import Workbook
from openpyxl.styles import Alignment
from io import BytesIO
from django.core.mail import EmailMessage


logger = logging.getLogger(__name__)

def validate_access_code(user, entered_code):
    try:
        access_code = AccessCode.objects.filter(user=user, code=entered_code).latest('created_at')
        if access_code.is_valid():
            access_code.delete()
            return True
    except AccessCode.DoesNotExist:
        pass
    return False


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def calcular_retraso(entrada, horario):
    entrada_time = entrada.hora_entrada.time()
    scheduled_start = horario.hora_entrada
    tolerance = timedelta(minutes=horario.tolerancia_retraso)
    scheduled_start_dt = timezone.make_aware(datetime.combine(entrada.hora_entrada.date(), scheduled_start))
    if entrada.hora_entrada > scheduled_start_dt + tolerance:
        entrada.es_retraso = True
        retraso = (entrada.hora_entrada - scheduled_start_dt).total_seconds() / 60
        entrada.minutos_retraso = int(retraso)







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
    
    today = timezone.now().date()
    assignment = get_today_assignment(request.user)
    
    if not assignment or not assignment.horario:
        messages.error(request, "No tienes un horario asignado para hoy.")
        return redirect('trabajador_home')
    
    if not request.user.puede_trabajar(today):
        messages.error(request, "No tienes permiso para trabajar hoy.")
        return redirect('trabajador_home')
    
    if RegistroEntrada.objects.filter(trabajador=request.user, hora_salida__isnull=True).exists():
        messages.error(request, 'Debes registrar la salida de tu entrada anterior antes de una nueva entrada')
        return redirect('trabajador_home')
    
    entradas_hoy = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_entrada__date=today
    ).count()
   
    if entradas_hoy >= 3:
        messages.error(request, 'Máximo 3 entradas diarias alcanzado')
        return redirect('trabajador_home')
    
    now = timezone.now()
    scheduled_start = datetime.combine(today, assignment.horario.hora_entrada)
    scheduled_start = timezone.make_aware(scheduled_start)
    tolerance = timedelta(minutes=assignment.horario.tolerancia_retraso)
    
    # Manejo de llegada temprana
    if now < scheduled_start - tolerance and 'accept_early' not in request.POST:
        messages.warning(request, "Estás llegando antes de tu horario. Esto no cuenta como horas extra.")
        context['early_arrival'] = True
        return render(request, 'home/users/trabajador_home.html', context)
    
    # Manejo de retraso
    elif now > scheduled_start + tolerance:
        if 'access_code' not in request.POST and not request.session.get('late_entry_allowed', False):
            LateArrivalNotification.objects.create(user=request.user)
            messages.warning(request, "Estás llegando tarde. Tu solicitud está en proceso. Por favor, espera unos momentos.")
            context['late_arrival'] = True
            return render(request, 'home/users/trabajador_home.html', context)
        elif 'access_code' in request.POST:
            entered_code = request.POST['access_code']
            if validate_access_code(request.user, entered_code):
                request.session['late_entry_allowed'] = True
                messages.success(request, "Código de acceso validado correctamente. Revisa tu correo.")
            else:
                messages.error(request, "Código de acceso inválido o expirado.")
                context['late_arrival'] = True
                return render(request, 'home/users/trabajador_home.html', context)
    
    # Procesar la entrada
    entrada = RegistroEntrada(trabajador=request.user, empresa=request.user.empresa)
    form = RegistroEntradaForm(request.POST or None, request.FILES or None, instance=entrada)
    
    if request.method == 'POST' and form.is_valid():
        metodo_seleccionado = form.cleaned_data['metodo']
        if metodo_seleccionado != request.user.metodo_registro_permitido:
            messages.error(request, 'No tienes habilitado este método de registro.')
            context['form_entrada'] = form
            return render(request, 'home/users/trabajador_home.html', context)
        
        entrada = form.save(commit=False)
        entrada.trabajador = request.user
        entrada.empresa = request.user.empresa
        
        if form.cleaned_data['metodo'] == 'geo':
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')
            if latitud and longitud:
                try:
                    latitud = float(latitud)
                    longitud = float(longitud)
                    if not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
                        raise ValueError("Coordenadas fuera de rango")
                    entrada.latitud = latitud
                    entrada.longitud = longitud
                except ValueError:
                    messages.error(request, 'Coordenadas inválidas')
                    context['form_entrada'] = form
                    return render(request, 'home/users/trabajador_home.html', context)
            else:
                messages.error(request, 'Geolocalización requerida')
                context['form_entrada'] = form
                return render(request, 'home/users/trabajador_home.html', context)
        
        entrada.save()
        if assignment.horario:
            calcular_retraso(entrada, assignment.horario)
            entrada.save()
        
        ip = get_client_ip(request)
        tipo = 'retraso' if entrada.es_retraso else 'entrada'
        Notificacion.objects.create(
            worker=request.user,
            tipo=tipo,
            ip_address=ip
        )
        
        if request.session.get('late_entry_allowed'):
            del request.session['late_entry_allowed']
        
        # Enviar correo de bienvenida
        subject = "Bienvenido - Registro de Entrada"
        message = f"Hola {request.user.get_full_name()},\n\nUsted ha registrado una entrada a las {entrada.hora_entrada.strftime('%H:%M')}.\n\n¡Que tengas un buen día!"
        send_mail(subject, message, 'from@example.com', [request.user.email], fail_silently=True)
        
        messages.success(request, 'Entrada registrada correctamente')
        return redirect('trabajador_home')
    else:
        if request.method == 'POST':
            messages.error(request, f'Error en el formulario: {form.errors.as_text()}')
        context['form_entrada'] = form
        return render(request, 'home/users/trabajador_home.html', context)








def calcular_horas_extra(entrada, horario):
    if entrada.hora_salida:
        scheduled_end = datetime.combine(entrada.hora_entrada.date(), horario.hora_salida)
        scheduled_end = timezone.make_aware(scheduled_end)
        tolerance_extra = timedelta(minutes=horario.tolerancia_horas_extra)
        if entrada.hora_salida > scheduled_end + tolerance_extra:
            entrada.es_horas_extra = True
            extra = (entrada.hora_salida - scheduled_end).total_seconds() / 60
            entrada.minutos_horas_extra = int(extra)







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
        if 'latitud_salida' in request.POST and 'longitud_salida' in request.POST:
            try:
                latitud_salida = float(request.POST['latitud_salida'])
                longitud_salida = float(request.POST['longitud_salida'])
                if (-90 <= latitud_salida <= 90) and (-180 <= longitud_salida <= 180):
                    entrada_activa.latitud_salida = latitud_salida
                    entrada_activa.longitud_salida = longitud_salida
                else:
                    messages.warning(request, 'Coordenadas de salida fuera de rango')
            except ValueError:
                messages.warning(request, 'Coordenadas de salida inválidas')
        
        assignment = get_today_assignment(request.user)
        if assignment and assignment.horario:
            calcular_horas_extra(entrada_activa, assignment.horario)
        entrada_activa.save()
        
        ip = get_client_ip(request)
        Notificacion.objects.create(
            worker=request.user,
            tipo='salida',
            ip_address=ip
        )
        
        # Generate Excel report
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de Asistencia"
        ws.append(["Día", "Hora de Entrada", "Método de Entrada", "Hora de Salida", "Método de Salida", "Horas Trabajadas"])
        
        horas_trabajadas = (entrada_activa.hora_salida - entrada_activa.hora_entrada).total_seconds() / 3600
        horas_trabajadas_redondeadas = round(horas_trabajadas)
        
        ws.append([
            entrada_activa.hora_entrada.date().strftime("%d/%m/%Y"),
            entrada_activa.hora_entrada.strftime("%H:%M"),
            entrada_activa.metodo,
            entrada_activa.hora_salida.strftime("%H:%M"),
            entrada_activa.metodo,  # Assuming same method for exit
            horas_trabajadas_redondeadas
        ])
        
        for row in ws.iter_rows(min_row=1, max_row=2):
            for cell in row:
                cell.alignment = Alignment(horizontal='center')
        
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        # Send email with report
        subject = "Reporte de Asistencia - Salida Registrada"
        message = f"Hola {request.user.get_full_name()},\n\nAdjunto tu reporte de asistencia de hoy.\n\nSaludos!"
        email = EmailMessage(subject, message, 'from@example.com', [request.user.email])
        email.attach('reporte_asistencia.xlsx', excel_file.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        
        messages.success(request, f'Salida registrada a las {entrada_activa.hora_salida.strftime("%H:%M")}')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('trabajador_home')






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





# DE AQUI EN ADELENTE ESTA TODO LO NUEVO 



def calcular_retraso(entrada, horario):
    from datetime import datetime
    hora_entrada_real = entrada.hora_entrada.time()
    hora_entrada_esperada = horario.hora_entrada
    if hora_entrada_real > hora_entrada_esperada:
        diferencia = (datetime.combine(datetime.min, hora_entrada_real) - 
                      datetime.combine(datetime.min, hora_entrada_esperada)).total_seconds() / 60
        if diferencia > horario.tolerancia_retraso:
            entrada.es_retraso = True
            entrada.minutos_retraso = int(diferencia - horario.tolerancia_retraso)


def calcular_horas_extra(salida, horario):
    from datetime import datetime
    hora_salida_real = salida.hora_salida.time()
    hora_salida_esperada = horario.hora_salida
    if hora_salida_real > hora_salida_esperada:
        diferencia = (datetime.combine(datetime.min, hora_salida_real) - 
                      datetime.combine(datetime.min, hora_salida_esperada)).total_seconds() / 60
        if diferencia > horario.tolerancia_horas_extra:
            salida.es_horas_extra = True
            salida.minutos_horas_extra = int(diferencia - horario.tolerancia_horas_extra)





