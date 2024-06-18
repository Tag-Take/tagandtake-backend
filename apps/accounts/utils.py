from datetime import datetime

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

def generate_activation_token(user):
    return default_token_generator.make_token(user)

def generate_activation_context(user):
    token = generate_activation_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    activation_url = f"{settings.FRONTEND_URL}/activate-user/{uid}/{token}/"

    context = {
        "user": user,
        "activation_url": activation_url,
        "current_year": datetime.now().year,
    }
    return context

def generate_password_reset_email_context(user):
    token = generate_activation_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

    context = {
        "user": user,
        "reset_url": reset_url,
        "current_year": datetime.now().year,
    }

    return context