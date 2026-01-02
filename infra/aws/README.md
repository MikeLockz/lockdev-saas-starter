# AWS Infrastructure - OpenTofu Configuration

This directory contains OpenTofu (Terraform) configuration for provisioning AWS resources required by the Lockdev SaaS application.

## Resources Managed

- **S3**: Document storage with encryption, versioning, and lifecycle policies
- **SES**: Email sending with DKIM, SPF, DMARC configuration
- **Route53**: DNS zone and records for domain verification
- **Secrets Manager**: Secure storage for credentials (GCP, Stripe, Sentry, etc.)
- **DynamoDB**: State locking table
- **SNS**: Bounce and complaint notifications for SES

## Prerequisites

1. **OpenTofu/Terraform**: Install OpenTofu (`brew install opentofu`) or Terraform
2. **AWS Credentials**: Configure AWS credentials with appropriate permissions
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```
3. **Domain Name**: You must own and be able to verify a domain for SES

## Initial Setup

### Step 1: Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
```

### Step 2: Initialize and Apply (First Time)

```bash
# Initialize OpenTofu
tofu init

# Review the plan
tofu plan

# Apply the configuration (creates S3 bucket and DynamoDB table for state)
tofu apply
```

### Step 3: Migrate to Remote State (Optional but Recommended)

After the initial apply creates the S3 bucket and DynamoDB table:

1. Uncomment the `backend "s3"` block in `backend.tf`
2. Update the bucket name, region, and table name to match your `terraform.tfvars`
3. Run:
   ```bash
   tofu init -migrate-state
   ```

## Verification

### Validate Configuration

```bash
# Check syntax
tofu validate

# Format files
tofu fmt

# Generate plan
tofu plan
```

### Verify SES Domain

After applying, you need to verify your domain with SES:

1. Check the DNS records created in Route53
2. Wait for DNS propagation (can take up to 48 hours)
3. Verify in AWS Console: SES > Verified Identities

### Update Secrets

The secrets created have placeholder values. Update them with actual credentials:

```bash
# Example: Update GCP credentials
aws secretsmanager put-secret-value \
  --secret-id lockdev-saas/dev/gcp-credentials \
  --secret-string file://path/to/service-account.json
```

## Security Notes

- **Never commit** `terraform.tfvars` or `*.tfstate` files
- All S3 buckets have public access blocked
- All secrets are encrypted at rest
- State file contains sensitive data - use S3 backend with encryption

## Outputs

After applying, you can view outputs:

```bash
tofu output

# View sensitive outputs
tofu output -json | jq
```

## Cleanup

To destroy all resources:

```bash
tofu destroy
```

> **Warning**: This will delete all AWS resources including S3 buckets and their contents. Use with caution.

## Troubleshooting

### SES Sandbox Mode

New AWS accounts start in SES sandbox mode. To send emails to non-verified addresses:

1. Go to AWS Console > SES
2. Request production access
3. Follow the verification process

### DNS Propagation

DNS changes can take time to propagate. Use these tools to check:

```bash
# Check DNS records
dig _amazonses.yourdomain.com TXT
dig _domainkey.yourdomain.com CNAME

# Or use online tools
# https://dnschecker.org
```

### State Lock Issues

If you encounter state lock errors:

```bash
# Force unlock (use with caution)
tofu force-unlock LOCK_ID
```

## Additional Resources

- [OpenTofu Documentation](https://opentofu.org/docs/)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [SES Setup Guide](https://docs.aws.amazon.com/ses/latest/dg/setting-up.html)
