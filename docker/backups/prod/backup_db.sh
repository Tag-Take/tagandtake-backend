#!/bin/bash

# Database Variables
DB_NAME="tagandtake_core"
DB_USER="postgres"
DB_CONTAINER="tagandtake-db"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_FILE="/tmp/${DB_NAME}-${TIMESTAMP}.sql.gz"
BUCKET_NAME="tagandtake-db-backups-prod"

# Step 1: Dump the database
echo "Starting backup of ${DB_NAME}..."
docker exec -t $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Step 2: Upload to S3
echo "Uploading ${BACKUP_FILE} to S3..."
aws s3 cp $BACKUP_FILE s3://$BUCKET_NAME/

# Step 3: Remove local backup
rm $BACKUP_FILE

echo "Backup completed and uploaded to S3."
