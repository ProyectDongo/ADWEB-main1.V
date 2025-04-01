"""
Django settings for sistema project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from django.conf import settings 
import os
from pathlib import Path
from dotenv import load_dotenv



# Ruta a wkhtmltopdf
#if os.name == 'nt':  # Windows
    #WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
#else:  # Unix
    #WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2z^3g8fdbrbm2^ixp+fhv#(!gtu%rfk2c4*(d5y_@=ki5amo0g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SESSION_EXPIRE_AT_BROWSER_CLOSE = True




# Application definition

INSTALLED_APPS = [
    'biometrics.apps.BiometricsConfig',
    'WEB',
    "anymail",
    'corsheaders',
    'django.contrib.admin', 
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'django_recaptcha',
    'widget_tweaks',
    'crispy_bootstrap5',
   
    

]
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap5',)

# Configuración CORS
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8001",
    "http://localhost:8001"
]



CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'content-type',
    'x-csrftoken',
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8001",
    "http://127.0.0.1:8001"
]
CORS_ALLOW_METHODS = [
    'GET',
    'OPTIONS',
    'POST',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    ]
SESSION_EXPIRE_SECONDS =  1000000000000000 # 20 minutos
SESSION_TIMEOUT_REDIRECT = 'login'
ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "WEB.views.scripts.context.context_processors.permisos_usuario",
                "WEB.views.scripts.context.context_processors.user_role",
            ],
        },
    },
]

#WSGI_APPLICATION = 'sistema.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydbd',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOGIN_REDIRECT_URL = 'redirect_after_login'  # Asegura que siempre pase por la función de redirección
LOGOUT_REDIRECT_URL = 'login_selector'  # Para que después del logout vuelva al login
 # Redirige a esta vista después del login
AUTH_USER_MODEL = 'WEB.Usuario'

#envios de correo
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP server
EMAIL_PORT = 587               # Port for TLS
EMAIL_USE_TLS = True
load_dotenv()  # Carga variables de .env

EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC")
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'biometrics.backends.FingerprintBackend',
]

ESSION_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Configuración de CAPTCHA
RECAPTCHA_PUBLIC_KEY = '321'
RECAPTCHA_PRIVATE_KEY = '0101'
RECAPTCHA_REQUIRED_SCORE = 0.85

# Rate limiting
RATELIMIT_ENABLE = True

CSRF_COOKIE_SECURE = False  # Solo para desarrollo
CSRF_COOKIE_HTTPONLY = False

CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False