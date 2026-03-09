# Backup and Recovery

## Backup Strategy

DualStack supports two database backends with different backup approaches:

| Backend | Backup Method | RPO | RTO |
|---------|---------------|-----|-----|
| **SQLite (self-hosted)** | `scripts/backup.sh` via cron | < 1 hour | < 4 hours |
| **PostgreSQL (production)** | `pg_dump` via cron or managed backups | < 1 hour | < 4 hours |
| **Turso (managed)** | Automatic (Turso platform) | Per SLA | Per SLA |

### SQLite Backup (Default)

The backup script creates consistent snapshots using `sqlite3 .backup`:

```bash
# Manual backup
./scripts/backup.sh

# Custom paths
./scripts/backup.sh /path/to/local.db /path/to/backups 48
```

**Cron schedule (hourly):**
```cron
0 * * * * /opt/dualstack/scripts/backup.sh /data/local.db /data/backups 48 >> /var/log/dualstack-backup.log 2>&1
```

### PostgreSQL Backup

For PostgreSQL deployments, use `pg_dump` for logical backups:

```bash
# Manual backup
pg_dump "$DATABASE_URL" --format=custom --file="backups/dualstack-$(date -u +%Y%m%dT%H%M%SZ).dump"

# Cron schedule (hourly)
0 * * * * pg_dump "$DATABASE_URL" --format=custom --file="/data/backups/dualstack-$(date -u +\%Y\%m\%dT\%H\%M\%SZ).dump" 2>> /var/log/dualstack-backup.log
```

Managed PostgreSQL services (Render, AWS RDS) provide automatic daily backups
with point-in-time recovery. These supplement but do not replace hourly backups.

---

## RPO and RTO Targets

### RPO: < 1 hour

**Recovery Point Objective** — maximum acceptable data loss.

- **Achieved by:** Hourly cron-based backups
- **Justification:** Hourly frequency means at most 59 minutes of data could
  be lost in a worst-case failure immediately before a backup runs
- **Enhancement path:** For near-zero RPO, add Litestream continuous
  replication (SQLite) or WAL archiving (PostgreSQL)

### RTO: < 4 hours

**Recovery Time Objective** — maximum acceptable downtime.

- **Achieved by:** Documented step-by-step restore procedure (below)
- **Justification:** Restore involves: identifying the backup (5 min),
  transferring the file (10 min), restoring (5 min), verifying (10 min),
  restarting services (10 min), plus buffer for diagnosis and decision-making
- **Requirement:** On-call responder must have access to backup storage
  and deployment infrastructure

---

## Retention Policy

| Tier | Frequency | Retention | Backups Kept |
|------|-----------|-----------|--------------|
| Hourly | Every hour | 48 hours | 48 |
| Daily | Once/day (optional) | 7 days | 7 |
| Weekly | Once/week (optional) | 4 weeks | 4 |

The default retention count is 48 (2 days of hourly backups). Adjust via the
third argument to `scripts/backup.sh`.

For S3 storage, configure lifecycle rules for longer retention:
```bash
export S3_BACKUP_BUCKET=s3://dualstack-backups/sqlite
./scripts/backup.sh
```

---

## Restore Procedure

### Step 1: Identify the Latest Backup

```bash
# List available backups (newest last)
ls -lt backups/*.db | head -10

# Or from S3
aws s3 ls s3://dualstack-backups/sqlite/ --human-readable
```

### Step 2: Verify Backup Integrity

```bash
sqlite3 backups/dualstack-YYYYMMDDTHHMMSSZ.db "PRAGMA integrity_check;"
# Expected output: ok
```

### Step 3: Stop the Application

```bash
docker compose stop backend
# or
systemctl stop dualstack-api
```

### Step 4: Restore the Database

```bash
# Back up the current (possibly corrupted) database
cp /data/local.db /data/local.db.damaged

# Restore from backup
cp backups/dualstack-YYYYMMDDTHHMMSSZ.db /data/local.db
```

For PostgreSQL:
```bash
pg_restore --dbname="$DATABASE_URL" --clean --if-exists backups/dualstack-YYYYMMDDTHHMMSSZ.dump
```

### Step 5: Verify the Restored Database

```bash
# Check integrity
sqlite3 /data/local.db "PRAGMA integrity_check;"

# Verify data is present
sqlite3 /data/local.db "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM items;"

# Check schema version matches
sqlite3 /data/local.db "SELECT version_num FROM alembic_version;"
```

### Step 6: Apply Missing Migrations (if needed)

If the backup predates a migration, apply it:
```bash
cd backend
alembic upgrade head
```

### Step 7: Restart the Application

```bash
docker compose up -d backend
# or
systemctl start dualstack-api
```

### Step 8: Verify Service Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

Monitor Grafana dashboards for 15 minutes to confirm normal operation.

---

## Monitoring Backups

### File-Based Monitoring

Check that backups are running and recent:

```bash
# Find most recent backup
LATEST=$(ls -t backups/*.db 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
    echo "ALERT: No backups found"
    exit 1
fi

# Check age (alert if older than 2 hours)
AGE_SECONDS=$(( $(date +%s) - $(stat -c%Y "$LATEST" 2>/dev/null || stat -f%m "$LATEST") ))
if [ "$AGE_SECONDS" -gt 7200 ]; then
    echo "ALERT: Latest backup is $(( AGE_SECONDS / 3600 )) hours old"
    exit 1
fi
```

### Prometheus Metrics (Future)

Add backup-specific metrics to enable Grafana alerting:
- `dualstack_backup_last_success_timestamp` — when the last backup completed
- `dualstack_backup_size_bytes` — size of the last backup
- `dualstack_backup_duration_seconds` — how long the backup took

### Alerts to Configure

- Backup age > 2 hours (backup not running)
- Backup size anomaly (>50% change from previous)
- Backup integrity check failure

---

## Testing Schedule

| Test | Frequency | Owner |
|------|-----------|-------|
| Run backup script manually | Monthly | On-call engineer |
| Full restore to staging | Quarterly | Engineering lead |
| Verify backup integrity | Weekly (automated) | Cron job |
| Update this document | After any backup infrastructure changes | Author |
