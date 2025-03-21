from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.FingerprintRegistrationView.as_view(), name='register'),  # Ruta limpia
    path('capture/', views.CaptureFingerprintView.as_view(), name='capture'),
    path('biometrics/logout/', views.fingerprint_logout, name='logout'),
]