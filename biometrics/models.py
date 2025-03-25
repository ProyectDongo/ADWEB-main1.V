
from django.db import models
from django.conf import settings

class UserFingerprint(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    template = models.BinaryField()
    quality = models.IntegerField()