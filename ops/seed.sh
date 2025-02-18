#!/bin/sh
set -e
echo "Running data synchronization tasks..."
python manage.py seed_categories_conditions
python manage.py seed_recall_reasons
python manage.py seed_payment_providers
python manage.py seed_store_supplies
echo "Data synchronization tasks completed."