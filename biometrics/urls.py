# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CaptureFingerprintView.as_view(), name='register'),
    path('biometrics/register/', views.FingerprintRegistrationView.as_view(), name='fingerprint_register'),
]