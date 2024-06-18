"""
Development 
"""

from .base import *
import os

# Enables debugging mode in development for error tracking.
DEBUG = True

# Allow Django to serve requests from any host.
ALLOWED_HOSTS = ["*"]

# DATABASES['default'].update(dj_database_url.parse(os.environ.get('DATABASE_URL')))

# URL to use when referring to static files.
STATIC_URL = "/static/"
# Defines the location in the filesystem where Django should look for static files.
STATICFILES_DIRS = [
    "static",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "tagandtake_core"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "123456"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# Configures email backend to print email to the console during development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

FRONTEND_URL = "http://localhost:3000"

# Basic logging configuration that logs errors to the console.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",  # Set higher level to reduce verbosity
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Only log INFO and above messages
        },
        # Optionally, add or modify other loggers if you know which one is responsible
    },
}

# Site ID
SITE_ID = 1

# Use console email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "no-reply@tagandtake.com"

# Session and CSRF cookies are not marked as secure during development as HTTPS is not typically enabled.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_SSL_REDIRECT = False

# HTTP Strict Transport Security is disabled in development.
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Specifies the default field type for model primary keys.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
