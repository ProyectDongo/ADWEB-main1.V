from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login, logout
import json
import requests
import logging
from .models import UserFingerprint

logger = logging.getLogger(__name__)

class FingerprintBaseView(View):
    API_URL = "http://localhost:52000/SGFDMSUWebAPI"  # URL local del servicio
    
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'API_KEY': 'H54180516911'  # Clave por defecto
        }

@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class CaptureFingerprint(FingerprintBaseView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            device_id = data.get('deviceId', 0)  # ID numérico según SDK
            quality = data.get('quality', 70)

            # Llamada al endpoint correcto
            api_response = requests.post(
                f"{self.API_URL}/CaptureFinger",  # Endpoint corregido
                headers=self.get_headers(),
                json={
                    "DeviceID": int(device_id),
                    "Quality": int(quality),
                    "TemplateFormat": "ISO",
                    "Timeout": 10000
                },
                timeout=15
            )
            
            api_response.raise_for_status()
            response_data = api_response.json()

            if response_data.get('ErrorCode') != 0:
                raise Exception(response_data.get('Message', 'Error en SecuGen'))

            return JsonResponse({
                "ErrorCode": 0,
                "Template": response_data['FingerData']  # Campo corregido
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            return JsonResponse(
                {"ErrorCode": 2, "Message": "Servicio SecuGen no disponible"},
                status=503
            )
        except Exception as e:
            logger.error(f"Error general: {str(e)}")
            return JsonResponse(
                {"ErrorCode": 3, "Message": str(e)},
                status=500
            )

@method_decorator(login_required, name='dispatch')
class FingerprintRegistrationView(FingerprintBaseView):
    def get(self, request):
        return render(request, 'biometrics/register_fingerprint.html')

    def post(self, request):
        try:
            data = json.loads(request.body)
            template1 = data.get('template1')
            template2 = data.get('template2')

            # Validación de templates ISO
            if len(template1) < 100 or len(template2) < 100:
                raise ValueError("Plantillas inválidas")

            response = requests.post(
                f"{self.API_URL}/Match",
                headers=self.get_headers(),
                json={
                    "Template1": template1,
                    "Template2": template2,
                    "TemplateFormat": "ISO"
                }
            )
            
            match_data = response.json()
            if match_data.get('Result', 0) == 1:  # Resultado booleano
                UserFingerprint.objects.update_or_create(
                    user=request.user,
                    defaults={'template': template1, 'quality': 100}
                )
                return JsonResponse({'status': 'success'})
            
            return JsonResponse({'status': 'no_match'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def fingerprint_logout(request):
    logout(request)
    return redirect('home')