from django.conf import settings
from apps.common.utils.email import send_email


def send_welcome_email(member):
    context = {
        "login_url": settings.LOGIN_URL,
        "how_it_works_url": settings.HOW_IT_WORKS_URL,
    }
    send_email(
        subject="Welcome to Tag&Take!",
        to=member.user.email,
        template_name="./welcome_email.html",
        context=context,
    )
