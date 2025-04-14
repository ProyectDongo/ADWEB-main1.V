from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CaptureFingerprintView.as_view(), name='register'),
    path('register-fingerprint/', views.FingerprintRegistrationView.as_view(), name='fingerprint_register'),
    path('check-fingerprint/', views.CheckFingerprintView.as_view(), name='check_fingerprint'),
    path('authenticate/', views.AuthenticateFingerprintView.as_view(), name='authenticate_fingerprint'),
    path('attendance/', views.AttendanceView.as_view(), name='attendance'),
    path('attendance-record/<int:user_id>/', views.AttendanceRecordView.as_view(), name='attendance_record'),
    path('generate-report/<int:user_id>/', views.GenerateReportView.as_view(), name='generate_report'),
]