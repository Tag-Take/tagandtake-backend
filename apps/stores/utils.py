import random
import string

from django.conf import settings

from apps.notifications.utils import send_email

def generate_pin():
    return ''.join(random.choices(string.digits, k=4))

def send_pin_email(store_profile):
    context = {
        'logo_url': settings.LOGO_URL,
        'pin': store_profile.pin,
    }
    send_email(
        subject="Your Store Profile PIN",
        to=store_profile.user.email,
        template_name="./send_pin.html",
        context=context,
    )

