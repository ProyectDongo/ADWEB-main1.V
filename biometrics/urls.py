from django.urls import path,include
from . import views

urlpatterns = [
    path('register/', views.CaptureFingerprintView.as_view(), name='register'),
    path('register-fingerprint/', views.FingerprintRegistrationView.as_view(), name='fingerprint_register'),
    path('authenticate/', views.AuthenticateFingerprintView.as_view(), name='authenticate_fingerprint'),
    path('attendance/', views.AttendanceView.as_view(), name='attendance'),


]