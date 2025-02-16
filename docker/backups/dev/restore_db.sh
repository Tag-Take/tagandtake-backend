#!/bin/bash

set -o pipefail  # Exit if any command in a pipeline fails
set -e  # Exit immediately if any command fails

# Database Variables
DB_NAME="tagandtake_core"
DB_USER="postgres"
DB_CONTAINER="tagandtake-backend-db-1"
BUCKET_NAME="tagandtake-db-backups-dev"

# Step 1: Check if PostgreSQL container is running
if ! docker ps --format '{{.Names}}' | grep -q "^$DB_CONTAINER$"; then
  echo "❌ Error: PostgreSQL container ($DB_CONTAINER) is not running."
  exit 1
fi

# Step 2: Find the latest backup
echo "Fetching the latest backup from S3..."
LATEST_BACKUP=$(aws s3 ls s3://$BUCKET_NAME/ | sort | tail -n 1 | awk '{print $4}')

if [ -z "$LATEST_BACKUP" ]; then
  echo "❌ Error: No backups found in S3 bucket $BUCKET_NAME."
  exit 1
fi

echo "📂 Latest backup found: $LATEST_BACKUP"

# Step 3: Download the latest backup
LOCAL_BACKUP_PATH="/tmp/$LATEST_BACKUP"

aws s3 cp "s3://$BUCKET_NAME/$LATEST_BACKUP" "$LOCAL_BACKUP_PATH"

# Step 4: Drop and recreate the database
echo "🚨 Dropping and recreating database before restore..."
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d postgres <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF

# Step 5: Restore the full dump
echo "♻️ Restoring database from $LATEST_BACKUP..."
if [[ "$LATEST_BACKUP" == *.gz ]]; then
  gunzip -c "$LOCAL_BACKUP_PATH" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
else
  cat "$LOCAL_BACKUP_PATH" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
fi

# Step 6: Cleanup local backup file (ALWAYS remove it)
rm -f "$LOCAL_BACKUP_PATH"

echo "✅ Full database restore completed successfully."
