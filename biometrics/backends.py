from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from .models import huellas
import base64
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

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
        

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()  
        if username is None or password is None:
            return None

        # Intentar autenticar primero por username
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            # Si no se encuentra por username, intentar por RUT
            try:
                user = UserModel.objects.get(rut=username)
            except UserModel.DoesNotExist:
                # Si no se encuentra ni por username ni por RUT, retornar None
                return None

        # Verificar la contraseña
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None