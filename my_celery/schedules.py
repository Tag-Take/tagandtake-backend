from celery.schedules import crontab

CELERY_SCHEDULES = {
    'apply-storage-fees-every-hour-6am-to-10pm': {
        'task': 'apps.marketplace.tasks.updates.apply_storage_fees_task',
        'schedule': crontab(minute=57, hour='6-22'),  
    },
}