from django.urls import path
from . import views


urlpatterns = [
   path('register/', views.CaptureFingerprintView.as_view(), name='register'),
    path('capture/', views.CaptureFingerprintView.as_view(), name='capture'),
    path('verify/', views.FingerprintRegistrationView.as_view(), name='verify'),
    ]