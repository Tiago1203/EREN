#!/bin/bash
# EREN Backup Script
# Version: 1.0.0

set -e

BACKUP_TYPE="${1:-full}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
BACKUP_DEST="${BACKUP_DEST:-s3://eren-backups}"

echo "========================================"
echo "EREN Backup"
echo "========================================"
echo "Backup Type: $BACKUP_TYPE"
echo "Retention: $RETENTION_DAYS days"
echo "Destination: $BACKUP_DEST"
echo "========================================"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="eren_backup_${TIMESTAMP}"

# Database backup
echo "[1/3] Backing up database..."
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > "/tmp/${BACKUP_NAME}_db.sql.gz"
echo "✅ Database backup: /tmp/${BACKUP_NAME}_db.sql.gz"

# Config backup
echo "[2/3] Backing up configuration..."
kubectl get configmap -n eren -o yaml > "/tmp/${BACKUP_NAME}_config.yaml"
kubectl get secret -n eren -o yaml > "/tmp/${BACKUP_NAME}_secrets.yaml"
echo "✅ Configuration backup completed"

# Upload to S3
echo "[3/3] Uploading to backup destination..."
aws s3 cp "/tmp/${BACKUP_NAME}_db.sql.gz" "${BACKUP_DEST}/"
aws s3 cp "/tmp/${BACKUP_NAME}_config.yaml" "${BACKUP_DEST}/"
echo "✅ Upload completed"

# Cleanup old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
aws s3 ls "$BACKUP_DEST/" | while read -r line; do
    BACKUP_DATE=$(echo "$line" | awk '{print $1}')
    BACKUP_NAME_S3=$(echo "$line" | awk '{print $4}')
    DAYS_OLD=$(($(date +%s) - $(date -d "$BACKUP_DATE" +%s) | bc) / 86400)
    if [ "$DAYS_OLD" -gt "$RETENTION_DAYS" ]; then
        aws s3 rm "${BACKUP_DEST}/${BACKUP_NAME_S3}"
        echo "Deleted old backup: $BACKUP_NAME_S3"
    fi
done

# Cleanup local files
rm -f "/tmp/${BACKUP_NAME}"_*.gz "/tmp/${BACKUP_NAME}"_*.yaml

echo "========================================"
echo "✅ Backup completed successfully!"
echo "Backup Name: $BACKUP_NAME"
echo "========================================"
