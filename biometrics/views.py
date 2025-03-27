from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import logging
import json
import base64
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import UserFingerprint
from WEB.models import *
import requests

logger = logging.getLogger(__name__)

class CaptureFingerprintView(View):
    def get(self, request):
        if request.user.role in ['supervisor', 'admin']:
            trabajadores = Usuario.objects.filter(role='trabajador', empresa=request.user.empresa)
            return render(request, 'biometrics/register_fingerprint.html', {'trabajadores': trabajadores})
        return render(request, 'biometrics/register_fingerprint.html')

class FingerprintRegistrationView(LoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse({'error': 'Método GET no permitido en esta ruta'}, status=405)



    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            template1 = data.get('template1')
            template2 = data.get('template2')
            match_score = data.get('match_score')

            if not all([template1, template2, match_score is not None]):
                return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

            if user_id:
                if request.user.role not in ['supervisor', 'admin']:
                    raise PermissionDenied("No tienes permiso para registrar huellas")
                try:
                    user_id = int(user_id)  
                    target_user = Usuario.objects.get(id=user_id, role='trabajador')
                except ValueError:
                    return JsonResponse({"error": "El user_id debe ser un número entero"}, status=400)
                except Usuario.DoesNotExist:
                    return JsonResponse({"error": "Usuario no encontrado o no es un trabajador"}, status=404)
            else:
                target_user = request.user  

            if match_score >= 100:
                template_bytes = base64.b64decode(template1)
                UserFingerprint.objects.update_or_create(
                    user=target_user,
                    defaults={'template': template_bytes, 'quality': 70}
                )
                return JsonResponse({"status": "success", "message": "Huella registrada"})
            else:
                return JsonResponse({"status": "no_match", "score": match_score})

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except PermissionDenied as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class AuthenticateFingerprintView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            captured_template = data.get('template')
            action = data.get('action', 'entrada')  # Por defecto es 'entrada' si no se especifica
            if not captured_template:
                return JsonResponse({"error": "Se requiere la plantilla de huella"}, status=400)

            captured_bytes = base64.b64decode(captured_template)

            for fp in UserFingerprint.objects.all():
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
                            return JsonResponse({"error": "Ya hay una entrada sin salida registrada"}, status=400)
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
                            'message': f'Entrada registrada para {user.username}',
                            'redirect': '/attendance/'
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
                            'message': f'Salida registrada para {user.username}',
                            'redirect': '/attendance/'
                        })
            return JsonResponse({'status': 'no_match', 'message': 'No se encontró coincidencia'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
class AttendanceView(View):
    def get(self, request):
        return render(request, 'biometrics/attendance.html')