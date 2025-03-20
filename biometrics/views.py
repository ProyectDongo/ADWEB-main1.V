from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.decorators import csrf
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
    API_URL = "http://localhost:52000/SGFDMSUWebAPI"
    
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'API_KEY': '846681907'  # Verificar en documentación SecuGen
        }

@method_decorator(csrf_exempt, name='dispatch')
class CaptureFingerprint(FingerprintBaseView):
    
    @method_decorator(login_required)
    def post(self, request):
        logger.info("Iniciando captura de huella")
        logger.debug(f"Body recibido: {request.body.decode()}")
        
        try:
            data = json.loads(request.body)
            device_id = data.get('deviceId', 0)
            quality = data.get('quality', 70)

            # Validación extendida de parámetros
            if not isinstance(device_id, int) or device_id < 0:
                raise ValueError("DeviceID inválido")
            
            if quality < 1 or quality > 100:
                raise ValueError("Calidad debe estar entre 1-100")

            # Verificar estado del servicio
            try:
                health_check = requests.get(
                    f"{self.API_URL}/GetDeviceInfo",
                    headers=self.get_headers(),
                    timeout=5
                )
                logger.debug(f"Respuesta health check: {health_check.text}")
            except Exception as e:
                logger.error(f"Health check fallido: {str(e)}")
                return JsonResponse(
                    {"ErrorCode": 5, "Message": "El servicio SecuGen no responde"},
                    status=503
                )

            # Captura de huella
            response = requests.post(
                f"{self.API_URL}/CaptureFinger",
                headers=self.get_headers(),
                json={
                    "DeviceID": device_id,
                    "Quality": quality,
                    "TemplateFormat": "ISO",
                    "Timeout": 15000
                },
                timeout=20
            )
            
            logger.debug(f"Respuesta cruda del API: {response.text}")
            
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('ErrorCode') != 0:
                error_msg = response_data.get('Message', 'Error desconocido en dispositivo')
                logger.error(f"Error del dispositivo: {error_msg}")
                return JsonResponse(
                    {"ErrorCode": response_data['ErrorCode'], "Message": error_msg},
                    status=400
                )

            return JsonResponse({
                "ErrorCode": 0,
                "Template": response_data.get('FingerData', '')
            })

        except json.JSONDecodeError as e:
            logger.error(f"Error JSON: {str(e)}")
            return JsonResponse(
                {"ErrorCode": 6, "Message": "Formato de datos inválido"},
                status=400
            )
        except requests.exceptions.Timeout:
            logger.error("Tiempo de espera agotado")
            return JsonResponse(
                {"ErrorCode": 7, "Message": "Tiempo de espera excedido"},
                status=504
            )
        except Exception as e:
            logger.exception("Error crítico en captura de huella")
            return JsonResponse(
                {"ErrorCode": 99, "Message": str(e)},
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

            if not template1 or not template2:
                raise ValueError("Faltan plantillas requeridas")

            # Validación de formato ISO
            if len(template1) < 100 or len(template2) < 100:
                logger.warning("Plantilla con formato inválido recibida")
                raise ValueError("Formato de plantilla inválido")

            # Verificar coincidencia
            match_response = requests.post(
                f"{self.API_URL}/Match",
                headers=self.get_headers(),
                json={
                    "Template1": template1,
                    "Template2": template2,
                    "TemplateFormat": "ISO"
                },
                timeout=15
            )
            
            match_data = match_response.json()
            logger.debug(f"Respuesta de coincidencia: {match_data}")
            
            if match_data.get('Result') == 1:
                UserFingerprint.objects.update_or_create(
                    user=request.user,
                    defaults={'template': template1, 'quality': 100}
                )
                return JsonResponse({'status': 'success', 'message': 'Huella registrada'})
            
            return JsonResponse({
                'status': 'error',
                'message': 'Las huellas no coinciden'
            }, status=400)

        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def fingerprint_logout(request):
    logout(request)
    return redirect('home')