# =============================================================================
# AWS CLOUDWATCH - Log Groups for Observability
# =============================================================================
# Centralized log aggregation from Aptible via Log Drain
# Logs are JSON-formatted from structlog for easy parsing

resource "aws_cloudwatch_log_group" "api" {
  name              = "/lockdev/${var.environment}/api"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.main.arn

  tags = {
    Environment = var.environment
    Service     = "api"
    ManagedBy   = "opentofu"
  }
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/lockdev/${var.environment}/worker"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.main.arn

  tags = {
    Environment = var.environment
    Service     = "worker"
    ManagedBy   = "opentofu"
  }
}

# =============================================================================
# IAM POLICY - Log Drain Write Access
# =============================================================================
# Aptible log drain needs permissions to write logs to CloudWatch

resource "aws_iam_policy" "log_drain" {
  name        = "lockdev-${var.environment}-log-drain"
  description = "Allow Aptible log drain to write logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          aws_cloudwatch_log_group.api.arn,
          "${aws_cloudwatch_log_group.api.arn}:*",
          aws_cloudwatch_log_group.worker.arn,
          "${aws_cloudwatch_log_group.worker.arn}:*"
        ]
      }
    ]
  })
}

# IAM User for Aptible log drain configuration
resource "aws_iam_user" "log_drain" {
  # checkov:skip=CKV_AWS_273:IAM user required for Aptible log drain integration
  name = "lockdev-${var.environment}-log-drain"

  tags = {
    Environment = var.environment
    Purpose     = "Aptible Log Drain"
    ManagedBy   = "opentofu"
  }
}

resource "aws_iam_user_policy_attachment" "log_drain" {
  # checkov:skip=CKV_AWS_40:Policy attachment to user required for Aptible log drain integration
  user       = aws_iam_user.log_drain.name
  policy_arn = aws_iam_policy.log_drain.arn
}

# Access key for Aptible configuration (store securely!)
resource "aws_iam_access_key" "log_drain" {
  user = aws_iam_user.log_drain.name
}

# =============================================================================
# OUTPUTS - For Aptible Log Drain Configuration
# =============================================================================

output "cloudwatch_log_drain_access_key_id" {
  description = "AWS Access Key ID for Aptible CloudWatch log drain"
  value       = aws_iam_access_key.log_drain.id
  sensitive   = false
}

output "cloudwatch_log_drain_secret_key" {
  description = "AWS Secret Access Key for Aptible CloudWatch log drain (SENSITIVE)"
  value       = aws_iam_access_key.log_drain.secret
  sensitive   = true
}

output "cloudwatch_api_log_group" {
  description = "CloudWatch Log Group name for API logs"
  value       = aws_cloudwatch_log_group.api.name
}

output "cloudwatch_worker_log_group" {
  description = "CloudWatch Log Group name for Worker logs"
  value       = aws_cloudwatch_log_group.worker.name
}
