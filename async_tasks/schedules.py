from celery.schedules import crontab

CELERY_SCHEDULES = {
    "apply-storage-fees-every-hour-6am-to-10pm": {
        "task": "apps.marketplace.tasks.updates.run_abandoned_item_updates",
        "schedule": crontab(minute=15, hour="6-22"),
    },
    "send-recalled-listing-collection-reminders-every-day": {
        "task": "apps.marketplace.tasks.reminders.run_recalled_listing_reminders",
        "schedule": crontab(minute=0, hour=9),
    },
}
