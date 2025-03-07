###################
#                 #
#   DEVELOPMENT   #
#                 #
###################

from .base import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enables debugging mode in development for error tracking.
DEBUG = True

# Allow Django to serve requests from any host.
ALLOWED_HOSTS = ["*"]
FRONTEND_URL = "http://localhost:3000"

# DATABASES['default'].update(dj_database_url.parse(os.environ.get('DATABASE_URL')))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("NAME", "tagandtake_core"),
        "USER": os.environ.get("USER", "postgres"),
        "PASSWORD": os.environ.get("PASSWORD", "123456"),
        "HOST": os.environ.get("HOST", "db"),
        "PORT": os.environ.get("PORT", "5432"),
    }
}



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

# Session and CSRF cookies are not marked as secure during development as HTTPS is not typically enabled.

SAME_SITE_COOKIE = None
# DOMAIN = "127.0.0.1"
DOMAIN = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_SECONDS = 0
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"


# HTTP Strict Transport Security is disabled in development.
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]

AUTH_COOKIE_SECURE = False

# AWS S3 settings
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")


AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
)
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
