from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import json
from .models import UserFingerprint

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class CaptureFingerprintView(View):
    def get(self, request):
        # Renderizamos la plantilla para capturar huellas desde el cliente
        return render(request, 'biometrics/register_fingerprint.html')

@method_decorator(csrf_exempt, name='dispatch')
class FingerprintRegistrationView(View):
    def post(self, request):
        try:
            # Recibimos las plantillas capturadas y el puntaje de coincidencia desde el cliente
            data = json.loads(request.body)
            template1 = data.get('template1')
            template2 = data.get('template2')
            match_score = data.get('match_score')

            if not template1 or not template2 or match_score is None:
                return JsonResponse({"error": "Se requieren ambas plantillas y el puntaje de coincidencia"}, status=400)

            # Verificamos si las huellas coinciden según el puntaje
            if match_score >= 100:  # Ajusta el umbral según necesites
                # Guardamos la plantilla en la base de datos asociada al usuario
                UserFingerprint.objects.update_or_create(
                    user=request.user,
                    defaults={'template': template1}
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