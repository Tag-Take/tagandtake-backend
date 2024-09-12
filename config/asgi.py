"""
ASGI config for tagandtake project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

ENV = os.environ.get("ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{ENV}")

application = get_asgi_application()


SECRET_KEY = "django-insecure-rkrbnj8+qgz(y%5l(9rrs%pnyfun^3gd9cg4b9#vy=xm+vmwn0"
