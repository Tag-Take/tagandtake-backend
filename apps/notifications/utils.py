# notifications/utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_email(subject, to, template_name, context, from_email=None):
    """
    Utility function to send emails using Django's built-in email backend.

    :param subject: Subject of the email.
    :param to: Recipient email address.
    :param template_name: Path to the email template.
    :param context: Context to render the template with.
    :param from_email: Sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=[to],
    )
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()
