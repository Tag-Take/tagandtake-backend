from premailer import transform
from celery import shared_task

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(
    subject: str,
    to: str,
    template_name: str,
    context=None,
    from_email=None,
    attachment=None,
):
    """
    Generic function to send emails using Django's built-in email backend.
    This function now sends the email asynchronously using a Celery task.

    :param subject: Subject of the email.
    :param to: Recipient email address.
    :param template_name: Path to the email template.
    :param context: Context to render the template with.
    :param from_email: Sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.
    """
    send_email_task.delay(subject, to, template_name, context, from_email, attachment)


@shared_task
def send_email_task(
    subject: str,
    to: str,
    template_name: str,
    context=None,
    from_email=None,
    attachment=None,
):
    """
    Celery task to send emails using Django's built-in email backend.

    :param subject: Subject of the email.
    :param to: Recipient email address.
    :param template_name: Path to the email template.
    :param context: Context to render the template with.
    :param from_email: Sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.
    """

    # Load CSS from the static directory
    css_path = staticfiles_storage.path("css/email_styles.css")
    with open(css_path, "r") as css_file:
        css_content = css_file.read().replace('"', "&quot;")

    # Update context with CSS content and logo URL
    if context is None:
        context = {}
    context.update(
        {
            "css": css_content,
        }
    )

    # Render the email template with the context
    html_message = render_to_string(template_name, context)
    html_message = transform(html_message, remove_classes=False)
    plain_message = strip_tags(html_message)
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    # Create and send the email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=[to],
    )
    email_message.attach_alternative(html_message, "text/html")

    if attachment:
        filename, file_content, mime_type = attachment
        email_message.attach(filename, file_content, mime_type)

    email_message.send()
