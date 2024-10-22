import os
import environ
from pathlib import Path
from datetime import timedelta

from async_tasks.schedules import CELERY_SCHEDULES

env = environ.Env()
environ.Env.read_env()


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-rkrbnj8+qgz(y%5l(9rrs%pnyfun^3gd9cg4b9#vy=xm+vmwn0",
)

DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_extensions",
    # internal apps
    "apps.accounts",
    "apps.notifications",
    "apps.items",
    "apps.marketplace",
    "apps.members",
    "apps.payments",
    "apps.stores",
    "apps.supplies",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "login": "20/minute",  # 5 login attempts per minute per IP (or per user if authenticated)
        "signup": "20/minute",  # 3 signups per hour per IP (or per user if authenticated)
        "password_reset": "20/hour",  # 5 password reset requests per hour per IP
        "resend_activation": "20/hour",  # 3 resend activation requests per hour per IP
    },
}

# Celery configuration
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

CELERY_BEAT_SCHEDULE = CELERY_SCHEDULES

SPECTAUCLAR_SETTINGS = {
    "TITLE": "Tag & Take API",
}


AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTHENTICATION_BACKENDS = [
    "apps.accounts.auth.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "max_similarity": 0.7,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# Stripe
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PLATFORM_WEBHOOK_SECRET = os.environ.get("STRIPE_PLATFORM_WEBHOOK_SECRET")
STRIPE_CONNECT_WEBHOOK_SECRET = os.environ.get("STRIPE_CONNECT_WEBHOOK_SECRET")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "AUTH_COOKIE_SAMESITE": "None",  # SameSite None for cross-origin requests
    "AUTH_COOKIE_SECURE": False,  # Only True in production (HTTPS)
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"


CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "withcredentials",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "apps/notifications/emails/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = ["./static/"]
STATIC_ROOT = BASE_DIR / "staticfiles"
TAG_FONT = STATICFILES_DIRS[0] + "fonts/Nunito-Bold.ttf"


# APP URLS
OPERATIONS_EMAIL = "info@tagandtake.com"
LOGO_URL = "https://your-logo-url.com/logo.png"
LOGIN_ROUTE = "/login"
HOW_IT_WORKS_ROUTE = "/how-it-works"
