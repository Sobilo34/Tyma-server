from .settings import *  # Import everything from base settings

import dj_database_url
import os

DEBUG = False

# Overriding the database for deployment
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# You might want to restrict hosts in production
ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME')]

# Static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security best practices for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
