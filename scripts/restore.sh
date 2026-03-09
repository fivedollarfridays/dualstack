#!/usr/bin/env bash
#
# DualStack Database Restore Script
#
# Restores a SQLite database from a backup file.
# Creates a safety backup of the current database before restoring.
# Validates the restored database with an integrity check.
#
# Usage:
#   ./scripts/restore.sh --backup-file backups/dualstack-20260309T120000Z.db
#   ./scripts/restore.sh --backup-file backups/latest.db --db-path /data/local.db
#
set -euo pipefail

# --- Configuration -----------------------------------------------------------

BACKUP_FILE=""
DB_PATH="${DB_PATH:-backend/local.db}"

# --- Parse arguments ---------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backup-file)
      BACKUP_FILE="$2"
      shift 2
      ;;
    --db-path)
      DB_PATH="$2"
      shift 2
      ;;
    *)
      echo "ERROR: Unknown option: $1" >&2
      echo "Usage: $0 --backup-file <path> [--db-path <path>]" >&2
      exit 1
      ;;
  esac
done

# --- Helpers -----------------------------------------------------------------

log() {
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] $*"
}

# --- Validation --------------------------------------------------------------

if [[ -z "$BACKUP_FILE" ]]; then
    echo "ERROR: --backup-file is required" >&2
    echo "Usage: $0 --backup-file <path> [--db-path <path>]" >&2
    exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE" >&2
    exit 1
fi

# Verify backup is a valid SQLite file
if ! sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" > /dev/null 2>&1; then
    echo "ERROR: Backup file is not a valid SQLite database: $BACKUP_FILE" >&2
    exit 1
fi

log "Restore started: backup=$BACKUP_FILE target=$DB_PATH"

# --- Safety backup of current database ---------------------------------------

if [[ -f "$DB_PATH" ]]; then
    TIMESTAMP=$(date -u '+%Y%m%dT%H%M%SZ')
    SAFETY_BACKUP="${DB_PATH}.pre-restore-${TIMESTAMP}"
    log "Creating safety backup of current database: $SAFETY_BACKUP"
    cp "$DB_PATH" "$SAFETY_BACKUP"
fi

# --- Restore -----------------------------------------------------------------

log "Restoring database from backup"
cp "$BACKUP_FILE" "$DB_PATH"

# --- Post-restore validation -------------------------------------------------

log "Validating restored database"
INTEGRITY=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>&1)
if [[ "$INTEGRITY" != "ok" ]]; then
    echo "ERROR: Restored database failed integrity check: $INTEGRITY" >&2
    # Restore the safety backup if validation fails
    if [[ -n "${SAFETY_BACKUP:-}" && -f "${SAFETY_BACKUP:-}" ]]; then
        log "Reverting to safety backup"
        cp "$SAFETY_BACKUP" "$DB_PATH"
    fi
    exit 1
fi

# Verify database has tables
TABLE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>&1)
if [[ "$TABLE_COUNT" -eq 0 ]]; then
    echo "ERROR: Restored database has no tables" >&2
    exit 1
fi

DB_SIZE=$(stat -c%s "$DB_PATH" 2>/dev/null || stat -f%z "$DB_PATH" 2>/dev/null)
log "Restore complete: $DB_PATH ($DB_SIZE bytes, $TABLE_COUNT tables, integrity: ok)"
