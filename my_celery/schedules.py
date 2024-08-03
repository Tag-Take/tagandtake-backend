from celery.schedules import crontab


CELERY_SCHEDULES = {
    'send-pickup-reminders-daily': {
        'task': 'items.tasks.reminders.tasks.send_pickup_reminders',
        'schedule': crontab(hour=7, minute=0),  # Every day at 7:00 AM
    },
    
}