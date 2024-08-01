import random
import string

from django.conf import settings

from apps.common.utils.email import send_email


def generate_pin():
    return "".join(random.choices(string.digits, k=4))


def send_welcome_email(store_profile):
    context = {
        "logo_url": settings.LOGO_URL,
        "pin": store_profile.pin,
    }
    send_email(
        subject="Welcome to Tag&Take",
        to=store_profile.user.email,
        template_name="./send_pin.html",
        context=context,
    )


def send_rest_pin_email(store_profile):
    context = {
        "logo_url": settings.LOGO_URL,
        "pin": store_profile.pin,
    }
    send_email(
        subject="New Tag&Take Store PIN",
        to=store_profile.user.email,
        template_name="./resend_pin.html",
        context=context,
    )
