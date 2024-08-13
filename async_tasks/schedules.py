from celery.schedules import crontab

CELERY_SCHEDULES = {
    "apply-storage-fees-every-hour-6am-to-10pm": {
        "task": "apps.marketplace.tasks.updates.apply_storage_fees_task",
        "schedule": crontab(minute=0, hour="6-22"),
    },
    "send-recalled-listing-collection-reminders-every-day": {
        "task": "apps.marketplace.tasks.reminders.run_storage_fee_reminder_checks",
        "schedule": crontab(minute=0, hour=10),
    },
}
