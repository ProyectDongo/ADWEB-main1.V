from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import requests
import logging
from urllib.parse import urlencode, parse_qs
from .models import UserFingerprint
from django.views.decorators.http import require_http_methods
logger = logging.getLogger(__name__)

class SecuGenAPI:
    BASE_URL = "http://localhost:8000"
    LICSTR = "846681907"

    @classmethod
    def capture_fingerprint(cls, timeout=10000, quality=70):
        endpoint = f"{cls.BASE_URL}/SGIFPCapture"
        params = {
            "Licstr": cls.LICSTR,
            "Timeout": timeout,
            "Quality": quality,
            "TemplateFormat": "ISO",
            "ImageWSQRate": "0.75"  # ⬅️ Usar string según doc
        }
        
        try:
            # Codificar parámetros correctamente
            encoded_params = urlencode(params, doseq=True)
            response = requests.post(
                endpoint,
                data=encoded_params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                verify=False
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error en SGIFPCapture: {str(e)}")
            return {"ErrorCode": 99, "Message": "Error de comunicación"}

    @classmethod
    def match_templates(cls, template1, template2):
        endpoint = f"{cls.BASE_URL}/SGIMatchScore"
        params = {
            "Licstr": cls.LICSTR,
            "Template1": template1,
            "Template2": template2,
            "TemplateFormat": "ISO"
        }
        
        try:
            encoded_params = urlencode(params, doseq=True)
            response = requests.post(
                endpoint,
                data=encoded_params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                verify=False
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error en SGIMatchScore: {str(e)}")
            return {"ErrorCode": 99, "Message": "Error en comparación"}

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class CaptureFingerprintView(View):
    @require_http_methods(["POST", "OPTIONS"])
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = 'http://localhost:8001'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        response['Access-Control-Max-Age'] = '86400'
        return response
    def post(self, request):
        try:
            # Parámetros obligatorios para SecuGen
            params = {
                "Licstr": "846681907",
                "Timeout": 10000,
                "Quality": 70,
                "TemplateFormat": "ISO",
                "ImageWSQRate": "0.75"
            }
            
            # Llamada CORRECTA a la API de SecuGen
            response = requests.post(
                "http://localhost:8000/SGIFPCapture",
                data=urlencode(params),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                verify=False
            )
            
            # Forzar decodificación UTF-8
            response.encoding = 'utf-8'  
            secugen_data = response.json()
            
            return JsonResponse(secugen_data)
            
        except Exception as e:
            return JsonResponse(
                {"ErrorCode": 99, "Message": str(e)},
                status=500
            )

    def _translate_error(self, error_code):
        error_map = {
            54: "Tiempo de espera agotado",
            55: "Dispositivo no encontrado",
            57: "Imagen inválida",
            10001: "Licencia inválida",
            # Agregar más códigos según documentación
        }
        return error_map.get(error_code, f"Error desconocido ({error_code})")

@method_decorator(login_required, name='dispatch')
class FingerprintRegistrationView(View):
    def get(self, request):  # Permite GET para cargar el template
        return render(request, 'biometrics/register_fingerprint.html')
    
    def post(self, request):
        template1 = request.session.get('captured_template')
        template2 = request.POST.get('template2')

        if not template1 or not template2:
            return JsonResponse({"error": "Faltan plantillas"}, status=400)

        match_result = SecuGenAPI.match_templates(template1, template2)
        
        if match_result.get("ErrorCode") != 0:
            return JsonResponse({
                "error": self._translate_error(match_result["ErrorCode"])
            }, status=400)

        if match_result.get("MatchingScore", 0) >= 100:  # Ajustar umbral según necesidades
            UserFingerprint.objects.update_or_create(
                user=request.user,
                defaults={'template': template1}
            )
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'no_match', "score": match_result["MatchingScore"]})

    def _translate_error(self, error_code):
        # Mapeo de errores de SGIMatchScore
        return "Error en comparación"

def fingerprint_logout(request):
    logout(request)
    return redirect('home')