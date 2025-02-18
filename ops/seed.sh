#!/bin/sh
set -e
echo "Running data synchronization tasks..."
python manage.py sync_categories_conditions
python manage.py sync_recall_reasons
python manage.py sync_payment_providers
python manage.py sync_store_supplies
echo "Data synchronization tasks completed."