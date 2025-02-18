from celery import shared_task

@shared_task
def backup_db():
    from django.core import management
    management.call_command("dbbackup")
