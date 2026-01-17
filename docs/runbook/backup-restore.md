# Backup and Restore Runbook

## Policy
- **Automated Backups:** Managed by Aptible for the primary PostgreSQL database.
- **Retention:** Backups are retained for 90 days.
- **Frequency:** Full daily backups with point-in-time recovery (PITR) support.
- **Scope:** Includes all PHI data, audit logs, and application state.

## Backup Verification
Backups must be verified monthly to ensure they are functional.

### Verification Procedure
1. Log into the Aptible Dashboard.
2. Select the relevant Environment.
3. Go to **Databases** > **[Database Name]** > **Backups**.
4. Verify that the "Latest Backup" is no older than 24 hours.
5. Perform a "Restore" to a *temporary* database in a staging environment.
6. Verify that the restored database is accessible and contains recent data.
7. Delete the temporary restored database.

## Database Restore (Incident Response)
In the event of data loss or corruption:

1. Identify the latest healthy backup timestamp in Aptible.
2. Use the **Restore** feature in Aptible to create a new database from that backup.
3. Update the `DATABASE_URL` environment variable for the `api` and `worker` services to point to the new database.
4. Restart the services.
5. Verify application health.

## S3 Data Backup
Files stored in S3 (e.g., uploaded documents) are protected by:
- **Versioning:** Enabled on all S3 buckets (see `infra/aws/s3.tf`).
- **Cross-Region Replication (Optional):** Can be enabled for disaster recovery.

### S3 Restore
1. Use the S3 Console to locate the previous version of a file.
2. Restore the desired version as the current version.
