#!/bin/bash

set -e  # Exit immediately if any command fails

# Database Variables
DB_NAME="tagandtake_core"
DB_USER="postgres"
DB_CONTAINER="tagandtake-backend-db-1"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_FILE="/tmp/${DB_NAME}-${TIMESTAMP}.sql.zst"
BUCKET_NAME="tagandtake-db-backups-dev"

# Step 1: Dump only the data (no schema, no roles) with efficient inserts
echo "📦 Starting data-only backup of ${DB_NAME}..."
docker exec -t $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME --data-only --disable-triggers --format=plain | zstd > $BACKUP_FILE

# Step 2: Upload to S3
echo "📤 Uploading ${BACKUP_FILE} to S3..."
aws s3 cp $BACKUP_FILE s3://$BUCKET_NAME/

# Step 3: Remove local backup file
rm -f $BACKUP_FILE

echo "✅ Backup completed and uploaded to S3."
