from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views import View
import json
import base64
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import *
from WEB.models import RegistroEntrada, Usuario
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

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
        
        return render(request, 'modules/biometrics/register_fingerprint.html', {
            'usuarios': usuarios,
            'selected_user': selected_user,
            'empresa_id': empresa.id,
            'vigencia_plan_id': request.user.vigencia_plan.id if request.user.vigencia_plan else None
        })

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
                    'http://localhost:9000/match',
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
                match_response = requests.post('http://localhost:9000/match', json={
                    'template1': base64.b64encode(stored_template).decode(),
                    'template2': captured_template
                })
                if match_response.ok and match_response.json()['score'] >= 100:
                    user = fp.user
                    today = timezone.now().date()
                    entries_today = RegistroEntrada.objects.filter(
                        trabajador=user,
                        hora_entrada__date=today
                    ).order_by('hora_entrada')

                    if action == 'entrada':
                        if entries_today.filter(hora_salida__isnull=True).exists():
                            return JsonResponse({"error": "Usted ya está ingresado hoy, debe registrar una salida primero"}, status=400)
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


class AttendanceView(View):
    def get(self, request):
        empresa = request.user.empresa
        return render(request, 'modules/biometrics/attendance.html', {
                'empresa_id': empresa.id,
                'vigencia_plan_id': request.user.vigencia_plan.id if request.user.vigencia_plan else None
            })
  
        
    
class AttendanceRecordView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        # Verifica permisos
        if request.user.role not in ['supervisor', 'admin']:
            return render(request, 'error/error.html')
        
        # Obtiene el usuario y sus registros
        user = get_object_or_404(Usuario, id=user_id, empresa=request.user.empresa)
        registros = RegistroEntrada.objects.filter(trabajador=user).order_by('-hora_entrada')
        
        # Calcula las horas totales para cada registro
        for registro in registros:
            if registro.hora_salida:
                diferencia = registro.hora_salida - registro.hora_entrada
                horas_totales = diferencia.total_seconds() / 3600  # Convierte segundos a horas
                registro.horas_totales = round(horas_totales, 2)  # Redondea a 2 decimales
            else:
                registro.horas_totales = None
        
        # Renderiza la plantilla con los datos
        return render(request, 'modules/biometrics/attendance_record.html', {
            'user': user,
            'registros': registros
        })


class GenerateReportView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        if request.user.role not in ['supervisor', 'admin']:
            return render(request, 'access_denied.html')
        user = get_object_or_404(Usuario, id=user_id, empresa=request.user.empresa)
        registros = RegistroEntrada.objects.filter(trabajador=user).order_by('-hora_entrada')

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título
        elements.append(Paragraph(f"Registro de Asistencia - {user.get_full_name()}", styles['Title']))

        # Tabla
        data = [['Fecha', 'Hora Entrada', 'Hora Salida', 'Horas Totales']]
        for reg in registros:
            fecha = reg.hora_entrada.strftime('%Y-%m-%d')
            entrada = reg.hora_entrada.strftime('%H:%M:%S')
            salida = reg.hora_salida.strftime('%H:%M:%S') if reg.hora_salida else 'N/A'
            horas = (reg.hora_salida - reg.hora_entrada).total_seconds() / 3600 if reg.hora_salida else 0
            data.append([fecha, entrada, salida, f"{horas:.2f}" if horas else 'N/A'])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="registro_asistencia_{user.username}.pdf"'
        return response