from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from .models import *
import base64

class FingerprintBackend(BaseBackend):
    def authenticate(self, request, fingerprint=None, **kwargs):
        try:
            fingerprint_bytes = base64.b64decode(fingerprint)
            return huellas.objects.select_related('user').get(
                template=fingerprint_bytes
            ).user
        except huellas.DoesNotExist:
            return None
        except Exception as e:
            return None

    def get_user(self, user_id):
        UserModel = settings.AUTH_USER_MODEL
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None