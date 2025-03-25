from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import logging
import json
import base64
from .models import UserFingerprint
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)

class CaptureFingerprintView(View):
    def get(self, request):
        return render(request, 'biometrics/register_fingerprint.html')

class FingerprintRegistrationView(LoginRequiredMixin, View):  # Requiere login
    def post(self, request):
        try:
            data = json.loads(request.body)
            template1 = data.get('template1')
            template2 = data.get('template2')
            match_score = data.get('match_score')

            if not all([template1, template2, match_score is not None]):
                return JsonResponse({"error": "Se requieren ambas plantillas y el puntaje de coincidencia"}, status=400)

            if match_score >= 100:  # Umbral ajustable
                template_bytes = base64.b64decode(template1)
                UserFingerprint.objects.update_or_create(
                    user=request.user,
                    defaults={'template': template_bytes, 'quality': 70}
                )
                return JsonResponse({'status': 'success', 'message': 'Huella registrada correctamente'})
            else:
                return JsonResponse({
                    'status': 'no_match',
                    'score': match_score,
                    'message': 'Las huellas no coinciden'
                })
        except Exception as e:
            logger.error(f"Error en el registro de huella: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)