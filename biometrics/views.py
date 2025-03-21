from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import requests
import logging
import json
from urllib.parse import urlencode, parse_qs
from .models import UserFingerprint
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
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
class CaptureFingerprintView(LoginRequiredMixin, View):
    login_url = '/login-selector/'
    
    def get(self, request):
        return render(request, 'biometrics/register_fingerprint.html')
    
    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "http://localhost:8001"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def post(self, request):
        try:
            params = {
                "Licstr": "846681907",
                "Timeout": 10000,
                "Quality": 70,
                "TemplateFormat": "ISO",
                "ImageWSQRate": "0.75"
            }
            
            response = requests.post(
                "http://localhost:8000/SGIFPCapture",
                data=urlencode(params),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                verify=False
            )
            
            response.encoding = 'utf-8'
            data = response.json()
            
            request.session['captured_template'] = data.get('TemplateBase64')
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Error crítico: {str(e)}", exc_info=True)
            return JsonResponse({"ErrorCode": 99, "Message": "Error interno"}, status=500)

@method_decorator(login_required, name='dispatch')
class FingerprintRegistrationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            template1 = request.session.get('captured_template')
            template2 = data.get('template2')
            
            # Validación
            if not template1 or not template2:
                return JsonResponse({"error": "Plantillas requeridas"}, status=400)
                
            # Lógica de comparación
            match_result = SecuGenAPI.match_templates(template1, template2)
            
            if match_result.get('ErrorCode', 0) != 0:
                return JsonResponse({"error": "Error en comparación"}, status=400)
                
            # Guardar huella si coincide
            if match_result.get('MatchingScore', 0) >= 100:
                UserFingerprint.objects.update_or_create(
                    user=request.user,
                    defaults={'template': template1}
                )
                return JsonResponse({'status': 'success'})
                
            return JsonResponse({'status': 'no_match', 'score': match_result['MatchingScore']})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def fingerprint_logout(request):
    logout(request)
    return redirect('home')