from celery.schedules import crontab

CELERY_SCHEDULES = {
    "apply-storage-fees-every-hour-6am-to-10pm": {
        "task": "apps.marketplace.tasks.updates.run_abandoned_item_updates",
        "schedule": crontab(minute=15, hour="*/1"),
    },
    "send-recalled-listing-collection-reminders-every-day": {
        "task": "apps.marketplace.tasks.reminders.run_recalled_listing_reminders",
        "schedule": crontab(minute=0, hour=11),
    },
    "run-item-transaction-cleanup-every-10-minutes": {
        "task": "apps.payments.tasks.transaction_cleanup_tasks.run_item_transaction_cleanup",
        "schedule": crontab(minute="*/1"),
    },
    "run-transaction-update-every-10-minutes": {
        "task": "apps.payments.tasks.transaction_cleanup_tasks.run_transaction_update",
        "schedule": crontab(minute="*/1"),
    },
    "run-pending-member-transfers-every-hour": {
        "task": "apps.payments.tasks.pending_transfer_tasks.run_pending_transfers",
        "schedule": crontab(minute=0, hour="*/1"),
    },
}
