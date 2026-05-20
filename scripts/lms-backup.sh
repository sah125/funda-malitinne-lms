#!/bin/bash
BACKUP_DIR="/backups/lms"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="funda_malitinne"
DB_USER="lms_user"
DB_PASSWORD="YOUR_DB_PASSWORD_HERE"

mkdir -p $BACKUP_DIR

export PGPASSWORD=$DB_PASSWORD
pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR/lms_$DATE.sql"
unset PGPASSWORD

# Keep 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "$DATE - Backup done" >> /var/log/lms-backup.log
