#!/bin/sh
set -e
echo "Restoring database from backup..."
python manage.py dbrestore 
echo "Database restored successfully."
