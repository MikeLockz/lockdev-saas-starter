#!/bin/bash
set -e

# Configuration
INFRA_DIR="infra/aws"

# Check for OpenTofu or Terraform
if command -v tofu &> /dev/null; then
    TF_CMD="tofu"
elif command -v terraform &> /dev/null; then
    TF_CMD="terraform"
else
    echo "Error: Neither 'tofu' nor 'terraform' found. Please install one to proceed."
    exit 1
fi

echo "========================================================"
echo "      Rotating Infrastructure Secrets (AWS IAM Keys)    "
echo "========================================================"
echo "Using command: $TF_CMD"
echo "Target Directory: $INFRA_DIR"
echo ""

# Navigate to infrastructure directory
cd "$INFRA_DIR"

echo "Step 1: Rotating AWS IAM Access Keys..."
echo " - Rotating: aws_iam_access_key.ses_smtp"
echo " - Rotating: aws_iam_access_key.log_drain"
echo ""

# Run the rotation
$TF_CMD apply \
    -replace=\"aws_iam_access_key.ses_smtp\" \
    -replace=\"aws_iam_access_key.log_drain\" \
    -auto-approve

echo ""
echo "========================================================"
echo "                Rotation Complete                       "
echo "========================================================"
echo ""

# Fetch outputs
echo "Fetching new credentials..."
OUTPUTS=$($TF_CMD output -json)

# Parse SES SMTP (Auto-managed)
SES_USER=$(echo "$OUTPUTS" | jq -r '.ses_smtp_username.value')
# Note: SES password is in Secrets Manager, but also outputted. We focus on where it goes.

# Parse Log Drain (Manual update required)
LOG_DRAIN_KEY=$(echo "$OUTPUTS" | jq -r '.cloudwatch_log_drain_access_key_id.value')
LOG_DRAIN_SECRET=$(echo "$OUTPUTS" | jq -r '.cloudwatch_log_drain_secret_key.value')

echo "--------------------------------------------------------"
echo "✅  1. SES SMTP Credentials"
echo "    Status: AUTOMATICALLY UPDATED in AWS Secrets Manager."
echo "    Action: No further action required for this key."
echo "    User: $SES_USER"
echo "--------------------------------------------------------"

echo "⚠️   2. Aptible Log Drain Credentials"
echo "    Status: ROTATED locally and in AWS."
echo "    Action: MANUAL UPDATE REQUIRED."
echo "    You must update your Aptible Log Drain configuration with these new credentials:"
echo ""
echo "    Access Key ID:     $LOG_DRAIN_KEY"
echo "    Secret Access Key: $LOG_DRAIN_SECRET"
echo "--------------------------------------------------------"
echo ""
echo "Run './scripts/rotate_infra_secrets.sh' anytime to rotate these keys again."
