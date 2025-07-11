
from .models import huellas
from users.models import Usuario
from ModuloAsistencia.models import RegistroEntrada
import requests
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views import View
from django.views.generic import ListView
import json
import base64
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import datetime, time
from django.utils.dateparse import parse_date





# captura de huella

 
class CaptureFingerprintView(View):
    def get(self, request):
        if request.user.role not in ['supervisor', 'admin']:
            return render(request, 'error/error.html')
        
        empresa = request.user.empresa
        usuarios = Usuario.objects.filter(empresa=empresa, role__in=['trabajador', 'supervisor'])
        selected_user_id = request.GET.get('user_id')
        
        selected_user = None
        if selected_user_id:
            try:
                selected_user = usuarios.get(id=selected_user_id)
            except Usuario.DoesNotExist:
                selected_user = None
        
        return render(request, 'Modulo_asistencia/biometrics/register_fingerprint.html', {
            'empresa': empresa,
            'usuarios': usuarios,
            'selected_user': selected_user,
            'empresa_id': empresa.id,
            'vigencia_plan_id': request.user.vigencia_plan.id if request.user.vigencia_plan else None
        })
    













# Huella Registration

class FingerprintRegistrationView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id') or str(request.user.id) 
            template1 = data.get('template1')
            template2 = data.get('template2')
            match_score = data.get('match_score')

            if not all([template1, template2, match_score is not None]):
                return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

            if user_id:
                if request.user.role not in ['supervisor', 'admin']:
                    raise PermissionDenied("No tienes permiso para registrar huellas")
                target_user = Usuario.objects.get(id=user_id)
                if target_user.empresa != request.user.empresa:
                    raise PermissionDenied("No puedes registrar huellas de usuarios de otras empresas")
            else:
                target_user = request.user

            if match_score >= 100:
                template_bytes = base64.b64decode(template1)
                empresa = request.user.empresa

                # Validación de huella duplicada
                existing_huellas = huellas.objects.filter(
                    user__empresa=empresa
                ).exclude(user=target_user)
                
                # Comparar con todas las huellas existentes
                for existing_huella in existing_huellas:
                    existing_template = base64.b64encode(existing_huella.template).decode('utf-8')
                    
                    try:
                        response = requests.post(
                            'http://localhost:9000/match',
                            json={
                                'template1': template1,
                                'template2': existing_template
                            },
                            timeout=2  # Timeout para no bloquear el proceso
                        )
                        
                        if response.status_code == 200:
                            match_data = response.json()
                            if match_data.get('score', 0) >= 100:
                                return JsonResponse({
                                    "error": "Esta huella ya está registrada para otro usuario"
                                }, status=400)
                                
                    except requests.exceptions.RequestException as e:
                        # Loggear error pero continuar con el proceso
                        print(f"Error al verificar huella: {str(e)}")

                # Si no hay coincidencias, guardar
                huellas.objects.update_or_create(
                    user=target_user,
                    defaults={'template': template_bytes, 'quality': 70}
                )
                return JsonResponse({"status": "success", "message": "Huella registrada correctamente"})
            else:
                return JsonResponse({"status": "no_match", "score": match_score})
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        















# Huella Authentication

class CheckFingerprintView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            template = data.get('template')
            
            if not template:
                return JsonResponse({"error": "Template faltante"}, status=400)
            
            empresa = request.user.empresa
            template_bytes = base64.b64decode(template)
            
            for huella in huellas.objects.filter(user__empresa=empresa):
                existing_template = base64.b64encode(huella.template).decode('utf-8')
                response = requests.post(
                    'http://host.docker.internal:9000/match',
                    json={'template1': template, 'template2': existing_template},
                    timeout=1
                )
                
                if response.status_code == 200 and response.json().get('score', 0) >= 100:
                    return JsonResponse({
                        "exists": True,
                        "user": huella.user.username
                    })
            
            return JsonResponse({"exists": False})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class AuthenticateFingerprintView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            captured_template = data.get('template')
            action = data.get('action', 'entrada')
            if not captured_template:
                return JsonResponse({"error": "Se requiere la plantilla de huella"}, status=400)

            captured_bytes = base64.b64decode(captured_template)

            for fp in huellas.objects.all():
                stored_template = fp.template
                match_response = requests.post('http://host.docker.internal:9000/match', json={
                    'template1': base64.b64encode(stored_template).decode(),
                    'template2': captured_template
                })
                if match_response.ok and match_response.json()['score'] >= 100:
                    user = fp.user
                    today = timezone.now().date()
                    start_of_day = timezone.make_aware(datetime.combine(today, time.min))
                    end_of_day = timezone.make_aware(datetime.combine(today, time.max))

                    entries_today = RegistroEntrada.objects.filter(
                        trabajador=user,
                        hora_entrada__range=(start_of_day, end_of_day)
                    ).order_by('hora_entrada')

                    if action == 'entrada':
                        if entries_today.filter(hora_salida__isnull=True).exists():
                            return JsonResponse({"error": "Ya está ingresado, registre una salida primero"}, status=400)
                        if entries_today.count() >= 3:
                            return JsonResponse({"error": "Máximo de 3 entradas por día alcanzado"}, status=400)
                        RegistroEntrada.objects.create(
                            trabajador=user,
                            metodo='huella',
                            huella_id='fingerprint_match',
                            empresa=user.empresa,
                            hora_entrada=timezone.now()
                        )
                        return JsonResponse({
                            'status': 'success',
                            'message': f'Entrada registrada para {user.username}'
                        })
                    elif action == 'salida':
                        last_entry = entries_today.filter(hora_salida__isnull=True).first()
                        if not last_entry:
                            return JsonResponse({"error": "No hay entrada previa para registrar salida"}, status=400)
                        if entries_today.filter(hora_salida__isnull=False).count() >= 3:
                            return JsonResponse({"error": "Máximo de 3 salidas por día alcanzado"}, status=400)
                        last_entry.hora_salida = timezone.now()
                        last_entry.save()
                        return JsonResponse({
                            'status': 'success',
                            'message': f'Salida registrada para {user.username}'
                        })
            return JsonResponse({'status': 'no_match', 'message': 'No se encontró coincidencia'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




# autenficacion de huella

class AttendanceView(View):
    def get(self, request):
        empresa = request.user.empresa
        return render(request, 'Modulo_asistencia/biometrics/attendance.html', {
               'empresa': empresa,
                'empresa_id': empresa.id,
                'vigencia_plan_id': request.user.vigencia_plan.id if request.user.vigencia_plan else None
            })
  
        
    



class AttendanceRecordView(LoginRequiredMixin, ListView):
    model = RegistroEntrada
    template_name = 'Modulo_asistencia/registro/attendance_record.html'
    context_object_name = 'registros'

    def get_queryset(self):
        trabajador = get_object_or_404(Usuario, id=self.kwargs['user_id'], empresa=self.request.user.empresa)
        queryset = RegistroEntrada.objects.filter(trabajador=trabajador)
        fecha_str = self.request.GET.get('fecha')
        if fecha_str:
            fecha = parse_date(fecha_str)
            if fecha:
                queryset = queryset.filter(hora_entrada__date=fecha)
        return queryset.order_by('hora_entrada')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trabajador = Usuario.objects.get(id=self.kwargs['user_id'])
        context['trabajador'] = trabajador
        context['empresa_id'] = self.request.user.empresa.id
        context['vigencia_plan_id'] = self.request.user.vigencia_plan.id if self.request.user.vigencia_plan else None

        for registro in context['registros']:
            # Calculate hours worked
            if registro.hora_salida:
                diferencia = registro.hora_salida - registro.hora_entrada
                total_seconds = int(diferencia.total_seconds())
                horas = total_seconds // 3600
                minutos = (total_seconds % 3600) // 60
                segundos = total_seconds % 60
                registro.horas_totales_str = f"{horas} h {minutos} min {segundos} s"
                if horas >= 8:
                    registro.horas_ordinarias_str = "8 h 0 min 0 s"
                    extra_seconds = total_seconds - (8 * 3600)
                    extra_horas = extra_seconds // 3600
                    extra_minutos = (extra_seconds % 3600) // 60
                    extra_segundos = extra_seconds % 60
                    registro.horas_extra_str = f"{extra_horas} h {extra_minutos} min {extra_segundos} s"
                else:
                    registro.horas_ordinarias_str = f"{horas} h {minutos} min {segundos} s"
                    registro.horas_extra_str = "0 h 0 min 0 s"
            else:
                registro.horas_totales_str = "N/A"
                registro.horas_ordinarias_str = "0 h 0 min 0 s"
                registro.horas_extra_str = "0 h 0 min 0 s"

            # Assign method display values
            registro.metodo_entrada_display = registro.get_metodo_display()
            registro.metodo_salida_display = registro.get_metodo_display() if registro.hora_salida else "N/A"

        fecha_str = self.request.GET.get('fecha')
        if fecha_str:
            fecha = parse_date(fecha_str)
            if fecha:
                context['fecha_seleccionada'] = fecha.strftime('%d/%m/%Y')

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['supervisor', 'admin']:
            return render(request, 'error/error.html')
        return super().dispatch(request, *args, **kwargs)











class GenerateReportView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        if request.user.role not in ['supervisor', 'admin']:
            return render(request, 'access_denied.html')

        user = get_object_or_404(Usuario, id=user_id, empresa=request.user.empresa)
        registros = RegistroEntrada.objects.filter(trabajador=user).order_by('hora_entrada')

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, 
                                pagesize=landscape(letter),
                                title=f"Asistencia {user.get_full_name()}",
                                author=request.user.empresa.nombre,
                                leftMargin=0.5*inch,
                                rightMargin=0.5*inch,
                                topMargin=0.5*inch,
                                bottomMargin=0.5*inch)

        elements = []
        styles = getSampleStyleSheet()

        # Estilo para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        )

        # Encabezado del documento
        elements.append(Paragraph(f"Libro de Asistencias - {user.get_full_name()}", title_style))
        elements.append(Spacer(1, 20))

        # Agrupar registros por mes y año
        from collections import defaultdict
        grouped = defaultdict(list)
        for reg in registros:
            key = reg.hora_entrada.strftime('%B %Y')
            grouped[key].append(reg)

        for mes, regs in grouped.items():
            elements.append(Paragraph(mes, styles['Heading2']))
            data = [
                ['Día', 'Hora Entrada (Método)', 'Hora Salida (Método)', 'Horas Trabajadas', 'Horas Ordinarias', 'Horas Extraordinarias']
            ]

            for reg in regs:
                dia = reg.hora_entrada.strftime('%d')
                entrada = f"{reg.hora_entrada.strftime('%H:%M:%S')} ({reg.get_metodo_display()})"
                salida = f"{reg.hora_salida.strftime('%H:%M:%S')} ({reg.get_metodo_display()})" if reg.hora_salida else '--:--:--'
                if reg.hora_salida:
                    diferencia = reg.hora_salida - reg.hora_entrada
                    horas_totales = diferencia.total_seconds() / 3600
                    horas_trabajadas = f"{horas_totales:.2f} h"
                    horas_ordinarias = f"{min(horas_totales, 8):.2f} h"
                    horas_extra = f"{max(horas_totales - 8, 0):.2f} h"
                else:
                    horas_trabajadas = 'N/A'
                    horas_ordinarias = '0 h'
                    horas_extra = '0 h'

                data.append([dia, entrada, salida, horas_trabajadas, horas_ordinarias, horas_extra])

            # Crear tabla con estilos
            table = Table(data, colWidths=[50, 150, 150, 100, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

        # Añadir leyenda
        footer_text = Paragraph(
            f"* Reporte generado automáticamente por el sistema de gestión {request.user.empresa.nombre}",
            ParagraphStyle(name='FooterStyle', fontSize=8, textColor=colors.grey, alignment=2)
        )
        elements.append(footer_text)

        # Generar PDF
        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="Asistencia_{user.username}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response