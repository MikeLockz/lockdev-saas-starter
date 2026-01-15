# Secrets Manager for sensitive credentials

# GCP Service Account Credentials (for Firebase/Vertex AI)
resource "aws_secretsmanager_secret" "gcp_credentials" {
  # checkov:skip=CKV2_AWS_57:Automatic rotation not applicable for GCP service account credentials
  name        = "${var.project_name}/${var.environment}/gcp-credentials"
  description = "GCP service account credentials for Firebase and Vertex AI"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "GCP Credentials"
    Description = "Service account JSON for Firebase Admin SDK and Vertex AI"
  }
}

# Placeholder secret version (must be updated manually with actual credentials)
resource "aws_secretsmanager_secret_version" "gcp_credentials" {
  secret_id = aws_secretsmanager_secret.gcp_credentials.id
  secret_string = jsonencode({
    type                        = "service_account"
    project_id                  = "REPLACE_WITH_ACTUAL_PROJECT_ID"
    private_key_id              = "REPLACE_WITH_ACTUAL_PRIVATE_KEY_ID"
    private_key                 = "REPLACE_WITH_ACTUAL_PRIVATE_KEY"
    client_email                = "REPLACE_WITH_ACTUAL_CLIENT_EMAIL"
    client_id                   = "REPLACE_WITH_ACTUAL_CLIENT_ID"
    auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
    token_uri                   = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url        = "REPLACE_WITH_ACTUAL_CERT_URL"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# SES SMTP Credentials
resource "aws_secretsmanager_secret" "ses_smtp" {
  # checkov:skip=CKV2_AWS_57:Automatic rotation not applicable for SES SMTP credentials
  name        = "${var.project_name}/${var.environment}/ses-smtp"
  description = "SES SMTP credentials for sending transactional emails"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "SES SMTP Credentials"
    Description = "SMTP username and password for SES"
  }
}

resource "aws_secretsmanager_secret_version" "ses_smtp" {
  secret_id = aws_secretsmanager_secret.ses_smtp.id
  secret_string = jsonencode({
    username = aws_iam_access_key.ses_smtp.id
    password = aws_iam_access_key.ses_smtp.ses_smtp_password_v4
  })
}

# Database Connection String (if needed for external access)
resource "aws_secretsmanager_secret" "database_url" {
  # checkov:skip=CKV2_AWS_57:Automatic rotation not applicable for database connection string
  name        = "${var.project_name}/${var.environment}/database-url"
  description = "PostgreSQL database connection string"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "Database URL"
    Description = "Connection string for PostgreSQL database"
  }
}

# Placeholder for database URL (must be updated with actual Aptible URL)
resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = jsonencode({
    url = "postgresql+asyncpg://user:password@host:5432/database"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# Stripe API Keys
resource "aws_secretsmanager_secret" "stripe" {
  # checkov:skip=CKV2_AWS_57:Automatic rotation not applicable for Stripe API keys
  name        = "${var.project_name}/${var.environment}/stripe"
  description = "Stripe API keys for payment processing"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "Stripe API Keys"
    Description = "Publishable and secret keys for Stripe"
  }
}

resource "aws_secretsmanager_secret_version" "stripe" {
  secret_id = aws_secretsmanager_secret.stripe.id
  secret_string = jsonencode({
    publishable_key = "REPLACE_WITH_STRIPE_PUBLISHABLE_KEY"
    secret_key      = "REPLACE_WITH_STRIPE_SECRET_KEY"
    webhook_secret  = "REPLACE_WITH_STRIPE_WEBHOOK_SECRET"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# Sentry DSN
resource "aws_secretsmanager_secret" "sentry" {
  # checkov:skip=CKV2_AWS_57:Automatic rotation not applicable for Sentry DSN
  name        = "${var.project_name}/${var.environment}/sentry"
  description = "Sentry DSN for error tracking"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "Sentry DSN"
    Description = "Data Source Name for Sentry error tracking"
  }
}

resource "aws_secretsmanager_secret_version" "sentry" {
  secret_id = aws_secretsmanager_secret.sentry.id
  secret_string = jsonencode({
    dsn = "REPLACE_WITH_SENTRY_DSN"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
