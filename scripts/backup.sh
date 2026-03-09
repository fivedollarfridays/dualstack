#!/usr/bin/env bash
#
# DualStack Database Backup Script
#
# Creates consistent SQLite backups using sqlite3 .backup command.
# Supports retention policy and optional S3 upload.
#
# Usage:
#   ./scripts/backup.sh                         # Uses defaults
#   ./scripts/backup.sh /path/to/db.sqlite      # Custom database path
#   ./scripts/backup.sh /path/to/db.sqlite /backups 48
#
# Cron example (hourly):
#   0 * * * * /opt/dualstack/scripts/backup.sh /data/local.db /data/backups 48
#
set -euo pipefail

# --- Configuration -----------------------------------------------------------

DB_PATH="${1:-backend/local.db}"
BACKUP_DIR="${2:-backups}"
RETAIN_COUNT="${3:-48}"           # Keep last N backups (48 = 2 days hourly)
S3_BUCKET="${S3_BACKUP_BUCKET:-}" # Optional: s3://bucket/prefix

# --- Helpers ------------------------------------------------------------------

log() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"
}

cleanup_old_backups() {
    local dir="$1"
    local keep="$2"
    local count
    count=$(find "$dir" -maxdepth 1 -name "*.db" -type f | wc -l)
    if [ "$count" -gt "$keep" ]; then
        local to_remove=$((count - keep))
        log "Retention: removing $to_remove old backup(s), keeping last $keep"
        ls -t "$dir"/*.db | tail -n "$to_remove" | xargs rm -f
    fi
}

# --- Main ---------------------------------------------------------------------

log "Starting backup: db=$DB_PATH dest=$BACKUP_DIR retain=$RETAIN_COUNT"

# Validate database exists
if [ ! -f "$DB_PATH" ]; then
    log "ERROR: Database file not found: $DB_PATH"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamped filename
TIMESTAMP=$(date -u '+%Y%m%dT%H%M%SZ')
BACKUP_FILE="${BACKUP_DIR}/dualstack-${TIMESTAMP}.db"

# Create consistent backup using sqlite3 .backup
log "Creating backup: $BACKUP_FILE"
sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# Verify backup integrity
log "Verifying backup integrity"
INTEGRITY=$(sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" 2>&1)
if [ "$INTEGRITY" != "ok" ]; then
    log "ERROR: Backup integrity check failed: $INTEGRITY"
    rm -f "$BACKUP_FILE"
    exit 2
fi

BACKUP_SIZE=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || stat -f%z "$BACKUP_FILE" 2>/dev/null)
log "Backup created: $BACKUP_FILE ($BACKUP_SIZE bytes)"

# Optional S3 upload
if [ -n "$S3_BUCKET" ]; then
    log "Uploading to S3: $S3_BUCKET"
    if aws s3 cp "$BACKUP_FILE" "${S3_BUCKET}/$(basename "$BACKUP_FILE")" --quiet; then
        log "S3 upload complete"
    else
        log "WARNING: S3 upload failed (backup retained locally)"
    fi
fi

# Prune old backups
cleanup_old_backups "$BACKUP_DIR" "$RETAIN_COUNT"

log "Backup complete"
