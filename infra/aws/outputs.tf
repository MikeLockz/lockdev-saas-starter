# S3 Outputs
output "documents_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  value       = aws_s3_bucket.documents.id
}

output "documents_bucket_arn" {
  description = "ARN of the S3 bucket for document storage"
  value       = aws_s3_bucket.documents.arn
}

output "state_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

# SES Outputs
output "ses_domain_identity" {
  description = "SES domain identity"
  value       = aws_ses_domain_identity.main.domain
}

output "ses_dkim_tokens" {
  description = "DKIM tokens for DNS configuration"
  value       = aws_ses_domain_dkim.main.dkim_tokens
}

output "ses_smtp_username" {
  description = "SMTP username for SES"
  value       = aws_iam_access_key.ses_smtp.id
  sensitive   = true
}

output "ses_smtp_password" {
  description = "SMTP password for SES"
  value       = aws_iam_access_key.ses_smtp.ses_smtp_password_v4
  sensitive   = true
}

output "ses_configuration_set" {
  description = "SES configuration set name"
  value       = aws_ses_configuration_set.main.name
}

# Secrets Manager Outputs
output "gcp_credentials_secret_arn" {
  description = "ARN of the GCP credentials secret"
  value       = aws_secretsmanager_secret.gcp_credentials.arn
}

output "ses_smtp_secret_arn" {
  description = "ARN of the SES SMTP credentials secret"
  value       = aws_secretsmanager_secret.ses_smtp.arn
}

output "database_url_secret_arn" {
  description = "ARN of the database URL secret"
  value       = aws_secretsmanager_secret.database_url.arn
}

output "stripe_secret_arn" {
  description = "ARN of the Stripe API keys secret"
  value       = aws_secretsmanager_secret.stripe.arn
}

output "sentry_secret_arn" {
  description = "ARN of the Sentry DSN secret"
  value       = aws_secretsmanager_secret.sentry.arn
}

# Route53 Outputs
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = local.zone_id
}

output "route53_name_servers" {
  description = "Route53 name servers (if zone was created)"
  value       = var.enable_route53 ? aws_route53_zone.main[0].name_servers : []
}

# DynamoDB Outputs
output "dynamodb_lock_table" {
  description = "DynamoDB table name for state locking"
  value       = aws_dynamodb_table.terraform_lock.name
}

# SNS Outputs
output "ses_bounces_topic_arn" {
  description = "ARN of the SES bounces SNS topic"
  value       = aws_sns_topic.ses_bounces.arn
}

output "ses_complaints_topic_arn" {
  description = "ARN of the SES complaints SNS topic"
  value       = aws_sns_topic.ses_complaints.arn
}

# Virus Scanner Outputs
output "quarantine_bucket_name" {
  description = "Name of the S3 bucket for quarantined files"
  value       = aws_s3_bucket.quarantine.id
}

output "quarantine_bucket_arn" {
  description = "ARN of the S3 bucket for quarantined files"
  value       = aws_s3_bucket.quarantine.arn
}

output "virus_scanner_function_name" {
  description = "Name of the Lambda virus scanner function"
  value       = aws_lambda_function.virus_scanner.function_name
}

output "virus_scanner_function_arn" {
  description = "ARN of the Lambda virus scanner function"
  value       = aws_lambda_function.virus_scanner.arn
}

output "virus_scanner_log_group" {
  description = "CloudWatch log group for virus scanner"
  value       = aws_cloudwatch_log_group.virus_scanner.name
}
