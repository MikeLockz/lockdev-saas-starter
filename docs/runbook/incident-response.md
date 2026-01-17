# Security Incident Response Runbook

## 1. Detection
Incidents may be detected via:
- Sentry alerts (Critical errors).
- CloudWatch Alarms.
- User reports.
- Unusual audit log patterns (e.g., mass READ_ACCESS).

## 2. Containment
### Compromised User Account
1. Disable the user in Firebase Console.
2. Revoke all active sessions in the database:
```sql
UPDATE user_sessions SET is_revoked = TRUE WHERE user_id = '[USER_ID]';
```

### Data Breach / Vulnerability
1. Identify affected service.
2. If necessary, put the app into maintenance mode by stopping the web/api services on Aptible.
3. Patch the vulnerability.

## 3. Investigation
1. Review `audit_logs` table for unauthorized access.
2. Filter by `actor_id` or `event_type`.
3. Check Sentry for traceback details.

## 4. Remediation
1. Apply security patches.
2. Rotate secrets if they were exposed (AWS Keys, Stripe Keys).
3. Notify the Compliance Officer.

## 5. Recovery
1. Restore services.
2. Monitor for recurrence.
