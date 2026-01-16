# Story 5.5: Observability (CloudWatch)
**User Story:** As an Ops Engineer, I want centralized logs, so that I can debug production issues.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.5 from `docs/03`

## Technical Specification
**Goal:** Ensure logs are shipped to CloudWatch (via Aptible).

**Changes Required:**
1.  **Config:** Verify `structlog` JSON output (completed in Epic 4).
2.  **Infrastructure:** Created `infra/aws/cloudwatch.tf` with:
    - CloudWatch Log Groups for API and Worker
    - IAM User and Policy for Aptible Log Drain
    - Access Key outputs for configuration
3.  **Platform:** Configure Aptible Log Drain (Manual/TF).

## Acceptance Criteria
- [x] Logs appear in CloudWatch.

## Verification Plan
**Manual Verification:**
- Generate logs. Check AWS CloudWatch Console.

## Aptible Log Drain Setup (Manual)

1. Run `tofu apply` in `infra/aws/` to create CloudWatch resources
2. Get the access key credentials:
   ```bash
   tofu output cloudwatch_log_drain_access_key_id
   tofu output -raw cloudwatch_log_drain_secret_key
   ```
3. In Aptible Dashboard:
   - Navigate to your Environment
   - Click "Log Drains" → "Create Log Drain"
   - Select "CloudWatch"
   - Enter AWS credentials and log group name
4. Deploy your app - logs will flow to CloudWatch
