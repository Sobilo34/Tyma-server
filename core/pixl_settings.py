from .settings import *  # Import everything from base settings

import dj_database_url
import os

# Production settings
DEBUG = False

# Database configuration - Pixl Space provides DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )
}

# Allowed hosts - allow Pixl Space domains
ALLOWED_HOSTS = [
    os.environ.get('PIXL_HOSTNAME', 'localhost'),
    '.pixl.space',
    '*.pixl.space',
    'localhost',
    '127.0.0.1',
]

# Add any custom domains from environment
if os.environ.get('CUSTOM_DOMAINS'):
    ALLOWED_HOSTS.extend(os.environ.get('CUSTOM_DOMAINS').split(','))

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://" + os.environ.get('PIXL_HOSTNAME', 'localhost'),
]

# Add custom origins if specified
if os.environ.get('CORS_ALLOWED_ORIGINS'):
    CORS_ALLOWED_ORIGINS.extend(os.environ.get('CORS_ALLOWED_ORIGINS').split(','))

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
