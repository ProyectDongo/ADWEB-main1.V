from django.urls import path
from .views import (
    CaptureFingerprint,
    FingerprintRegistrationView,
  
    fingerprint_logout
)

urlpatterns = [
   path('capture/', CaptureFingerprint.as_view(), name='capture'),
   path('register/', FingerprintRegistrationView.as_view(), name='register'),

    path('logout/', fingerprint_logout, name='fingerprint_logout'),
]