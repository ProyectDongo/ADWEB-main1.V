
from django.conf import settings
from django.db import models

class UserFingerprint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    template = models.TextField()
    quality = models.IntegerField()
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.registered_at}"