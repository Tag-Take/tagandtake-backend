#!/bin/bash

# Database Variables
DB_NAME="tagandtake_core"
DB_USER="postgres"
DB_CONTAINER="tagandtake-db"
BUCKET_NAME="tagandtake-db-backups-staging"

# Step 1: Find the latest backup
echo "Fetching the latest backup from S3..."
LATEST_BACKUP=$(aws s3 ls s3://$BUCKET_NAME/ | sort | tail -n 1 | awk '{print $4}')

# Step 2: Download the latest backup
aws s3 cp s3://$BUCKET_NAME/$LATEST_BACKUP /tmp/$LATEST_BACKUP

# Step 3: Restore the database
echo "Restoring database from $LATEST_BACKUP..."
gunzip < /tmp/$LATEST_BACKUP | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME

# Step 4: Cleanup local backup file
rm /tmp/$LATEST_BACKUP

echo "Database restore completed."
