"""
Django settings for SRTimeWeb project.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = True
CUSTOM_PORT = os.getenv('DJANGO_PORT', '9000')
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'core',
    'devices',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CSRF disabled for API: Using JWT authentication (stateless, no CSRF needed)
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom logging middleware (after auth to capture user context)
    'core.middlewares.logging_middleware.RequestLoggingMiddleware',
    'core.middlewares.logging_middleware.ErrorCaptureMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'static'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'srtimeweb'),
        'USER': os.getenv('POSTGRES_USER', 'srtimeweb_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = None

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# SECURITY SETTINGS - DEVELOPMENT MODE
# ============================================================================
# ⚠️ WARNING: Current settings are configured for DEVELOPMENT ONLY
# For PRODUCTION deployment, review and update ALL settings marked with [PROD]
# ============================================================================

# CORS Configuration
# [DEV] Allow all origins for development convenience
CORS_ALLOW_ALL_ORIGINS = True  # [PROD] Set to False and use CORS_ALLOWED_ORIGINS list
# [PROD] Uncomment and configure:
# CORS_ALLOWED_ORIGINS = [
#     'https://yourdomain.com',
#     'https://www.yourdomain.com',
# ]
CORS_ALLOW_CREDENTIALS = True  # Required for CSRF token cookies

# CSRF Configuration
# [DEV] Trust local development servers
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000', 
    'http://127.0.0.1:3000', 
    'http://localhost:9000', 
    'http://127.0.0.1:9000'
]
# [PROD] Replace with production domains:
# CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com', 'https://www.yourdomain.com']

# [DEV] Allow JavaScript to read CSRF token (required for React/SPA)
CSRF_COOKIE_HTTPONLY = False  
# [PROD] Consider keeping False if using SPA, or implement alternative CSRF strategy

# [DEV] Lax allows cookies in some cross-site requests
CSRF_COOKIE_SAMESITE = 'Lax'  
# [PROD] Consider 'Strict' for maximum security, or keep 'Lax' for better UX

# [DEV] Secure flag disabled for local HTTP development
CSRF_COOKIE_SECURE = False  
# [PROD] MUST set to True when using HTTPS in production

# Additional Production Security Settings to Enable:
# [PROD] Uncomment these for production:
# SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
# SESSION_COOKIE_SECURE = True  # Only send session cookie over HTTPS
# SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS filter
# SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
# SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security (1 year)
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# ============================================================================

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
# ATTENDANCE ENGINE SHADOW MODE
# Enable dual-engine validation: V1 (production) + V2 (shadow validation)
# Shadow mode runs V2 in parallel without affecting production data
ATTENDANCE_SHADOW_ENABLED = os.getenv('ATTENDANCE_SHADOW_ENABLED', 'True').lower() == 'true'
ATTENDANCE_SHADOW_LOG_LEVEL = os.getenv('ATTENDANCE_SHADOW_LOG_LEVEL', 'WARNING')  # DEBUG, INFO, WARNING, ERROR

# Shadow mode behavior:
# - V1 (attendance_engine.py) → Production calculations (official record)
# - V2 (attendance_engine_v2.py) → Validation calculations (shadow)
# - Both use unified resolver (schedule_resolver.py) → Guaranteed consistency
# - Differences are logged to 'attendance.shadow.*' loggers

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create logs directory if doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [{name}] {module}.{funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {asctime} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_attendance': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'attendance.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_api': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'api.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        # Django core loggers
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file_errors'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        # Application-specific loggers
        'core': {
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'devices': {
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        # Attendance engine loggers
        'attendance': {
            'handlers': ['console', 'file_attendance', 'file_errors'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'attendance.shadow': {
            'handlers': ['file_attendance'],
            'level': ATTENDANCE_SHADOW_LOG_LEVEL,
            'propagate': False,
        },
        'attendance.resolver': {
            'handlers': ['file_attendance'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        # API request/response logging
        'api': {
            'handlers': ['console', 'file_api', 'file_errors'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file_general', 'file_errors'],
        'level': 'INFO',
    },
}

# ============================================================================
# LOGGING NOTES
# ============================================================================
# Available log files:
# - logs/django.log      → General application logs (INFO+)
# - logs/errors.log      → Error and exception logs (ERROR+)
# - logs/attendance.log  → Attendance engine and shadow mode logs (DEBUG+)
# - logs/api.log         → API request/response logs (INFO+)
#
# Usage in code:
#   import logging
#   logger = logging.getLogger('core')  # or 'attendance', 'api', etc.
#   logger.debug('Debug message')
#   logger.info('Info message')
#   logger.warning('Warning message')
#   logger.error('Error message', exc_info=True)  # Include traceback
#   logger.critical('Critical message')
#
# Log rotation: Each file max 10MB, keeps 5 backups
# ============================================================================