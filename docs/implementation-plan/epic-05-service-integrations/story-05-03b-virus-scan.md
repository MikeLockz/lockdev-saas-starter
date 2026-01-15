# Story 5.3b: Virus Scanning (AWS Lambda)
**User Story:** As a Security Engineer, I want all uploads scanned for malware, so that the platform remains safe.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.3b from `docs/03`

## Technical Specification
**Goal:** Deploy Virus Scan Lambda.

**Changes Required:**
1.  **Infra:** `infra/aws/lambda-virus-scan.tf`
    - Lambda + ClamAV layer.
    - S3 Event Trigger.
    - Quarantine bucket logic.

## Implementation Notes
**Files Created:**
- `infra/aws/lambda-virus-scan.tf` - Terraform configuration for Lambda, quarantine bucket, IAM roles, and S3 triggers
- `infra/aws/lambda-virus-scan/index.py` - Python Lambda function with ClamAV integration
- `infra/aws/lambda-virus-scan/README.md` - Deployment and testing documentation
- `infra/aws/lambda-virus-scan/requirements.txt` - Python dependencies
- `infra/aws/package-lambda.sh` - Deployment packaging script
- `infra/aws/outputs.tf` - Added outputs for quarantine bucket and Lambda function

**Key Features:**
- Automatic virus scanning on S3 object creation
- ClamAV integration with virus definition updates
- Infected files moved to quarantine bucket
- Clean files tagged with `scan-status=clean`
- Error handling and CloudWatch logging
- HIPAA-compliant encryption and access controls

## Acceptance Criteria
- [x] Infrastructure code created for Lambda virus scanner
- [x] Quarantine bucket configured with encryption and versioning
- [x] S3 event trigger configured to invoke Lambda on upload
- [ ] EICAR test file is moved to quarantine (requires deployment)
- [ ] Clean file is tagged `scan-status=clean` (requires deployment)

## Verification Plan
**Manual Verification:**
- Upload EICAR file. Verify it moves to quarantine bucket.
- Upload clean file. Verify it is tagged as clean.

**Note:** Full verification requires:
1. Building or obtaining a ClamAV Lambda layer
2. Updating `lambda-virus-scan.tf` with the layer ARN
3. Running `./package-lambda.sh` to create deployment package
4. Applying Terraform configuration: `tofu init && tofu apply`
5. Following test procedures in `lambda-virus-scan/README.md`

