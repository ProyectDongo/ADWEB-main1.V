from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from .models import UserFingerprint

class FingerprintBackend(BaseBackend):
    def authenticate(self, request, fingerprint=None, **kwargs):
        try:
            return UserFingerprint.objects.select_related('user').get(
                template=fingerprint
            ).user
        except UserFingerprint.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = settings.AUTH_USER_MODEL
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None