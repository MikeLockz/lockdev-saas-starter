# SES Domain Identity
resource "aws_ses_domain_identity" "main" {
  domain = var.domain_name
}

# DKIM signing configuration
resource "aws_ses_domain_dkim" "main" {
  domain = aws_ses_domain_identity.main.domain
}

# Email from address
resource "aws_ses_email_identity" "noreply" {
  email = "noreply@${var.domain_name}"
}

# Configuration set for tracking
resource "aws_ses_configuration_set" "main" {
  name = "${var.project_name}-${var.environment}"

  delivery_options {
    tls_policy = "Require"
  }

  reputation_metrics_enabled = true
}

# SNS topic for bounce notifications
resource "aws_sns_topic" "ses_bounces" {
  name = "${var.project_name}-ses-bounces-${var.environment}"

  tags = {
    Name        = "SES Bounce Notifications"
    Description = "SNS topic for SES bounce notifications"
  }
}

# SNS topic for complaint notifications
resource "aws_sns_topic" "ses_complaints" {
  name = "${var.project_name}-ses-complaints-${var.environment}"

  tags = {
    Name        = "SES Complaint Notifications"
    Description = "SNS topic for SES complaint notifications"
  }
}

# Event destination for bounces
resource "aws_ses_event_destination" "bounces" {
  name                   = "bounces"
  configuration_set_name = aws_ses_configuration_set.main.name
  enabled                = true
  matching_types         = ["bounce"]

  sns_destination {
    topic_arn = aws_sns_topic.ses_bounces.arn
  }
}

# Event destination for complaints
resource "aws_ses_event_destination" "complaints" {
  name                   = "complaints"
  configuration_set_name = aws_ses_configuration_set.main.name
  enabled                = true
  matching_types         = ["complaint"]

  sns_destination {
    topic_arn = aws_sns_topic.ses_complaints.arn
  }
}

# IAM user for SMTP credentials
resource "aws_iam_user" "ses_smtp" {
  name = "${var.project_name}-ses-smtp-${var.environment}"

  tags = {
    Name        = "SES SMTP User"
    Description = "IAM user for SES SMTP authentication"
  }
}

# IAM policy for sending emails
resource "aws_iam_user_policy" "ses_smtp" {
  name = "ses-send-email"
  user = aws_iam_user.ses_smtp.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# Access key for SMTP (credentials stored in Secrets Manager)
resource "aws_iam_access_key" "ses_smtp" {
  user = aws_iam_user.ses_smtp.name
}
