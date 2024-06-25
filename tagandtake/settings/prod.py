"""
Production
"""
from .base import *
import os

# Debugging is disabled in production for security reasons.
DEBUG = False

# Only requests to your production domain are allowed.
ALLOWED_HOSTS = ["your-production-domain.com"]

# Database configuration uses environment variables for security.
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


FRONTEND_URL = "https://tagandtake.com"

SITE_ID = 1
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.your_email_service.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "info@tagandtake.com"
EMAIL_HOST_PASSWORD = "password"
DEFAULT_FROM_EMAIL = "info@tagandtake.com"


# Email backend configuration for sending emails.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yourmailprovider.com"  # The host to use for sending email.
EMAIL_PORT = 587  # Port to use for the SMTP server.
EMAIL_USE_TLS = (
    True  # Whether to use a TLS (secure) connection when talking to the SMTP server.
)
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]  # Username to use for the SMTP server.
EMAIL_HOST_PASSWORD = os.environ[
    "EMAIL_HOST_PASSWORD"
]  # Password to use for the SMTP server.

# Logging configuration to capture warnings and errors.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "/path/to/your/logs/django_error.log",  # Path to where the log file should be saved.
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# Security settings to enhance application security.
SESSION_COOKIE_SECURE = (
    True  # Marks the session cookie as secure (transmitted only over HTTPS).
)
CSRF_COOKIE_SECURE = True  # Marks the CSRF cookie as secure.
SECURE_BROWSER_XSS_FILTER = (
    True  # Enables the browser's XSS filtering and forces it to be active.
)
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevents the browser from MIME-sniffing a response away from the declared content-type.
SECURE_SSL_REDIRECT = True  # Redirects all non-HTTPS requests to HTTPS.

# HTTP Strict Transport Security: Tells browsers that the site should only be accessed using HTTPS, not HTTP.
SECURE_HSTS_SECONDS = (
    31536000  # Number of seconds that the HSTS header should be set on responses.
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    True  # If True, this rule applies to all subdomains as well.
)
SECURE_HSTS_PRELOAD = (
    True  # If True, the site will be included in the preload list for HSTS.
)
SAME_SITE_COOKIE = "Strict" 

