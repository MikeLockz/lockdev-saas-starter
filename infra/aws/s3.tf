# S3 bucket for document storage
resource "aws_s3_bucket" "documents" {
  # checkov:skip=CKV_AWS_144:Cross-region replication not required for starter kit
  # checkov:skip=CKV_AWS_18:Logging enabled via separate aws_s3_bucket_logging resource
  # checkov:skip=CKV2_AWS_62:Event notifications configured separately via aws_s3_bucket_notification
  bucket = "${var.project_name}-documents-${var.environment}"

  tags = {
    Name        = "Document Storage"
    Description = "S3 bucket for storing patient documents and PHI"
    Compliance  = "HIPAA"
  }
}

# Enable versioning for document history
resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption (HIPAA requirement)
resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
    bucket_key_enabled = true
  }
}

# Block all public access (HIPAA requirement)
resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CORS configuration for frontend uploads
resource "aws_s3_bucket_cors_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://*.lockdev.com", "http://localhost:5173"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Lifecycle policy for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }

  rule {
    id     = "delete-incomplete-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Access logging bucket
resource "aws_s3_bucket" "access_logs" {
  # checkov:skip=CKV_AWS_144:Cross-region replication not required for starter kit
  # checkov:skip=CKV2_AWS_61:Lifecycle configuration not required for access logs bucket
  # checkov:skip=CKV2_AWS_62:Event notifications not required for access logs bucket
  # checkov:skip=CKV_AWS_145:Using KMS encryption, but not required for access logs
  # checkov:skip=CKV_AWS_18:Self-logging bucket - would create circular dependency
  bucket = "${var.project_name}-access-logs-${var.environment}"

  tags = {
    Name        = "S3 Access Logs"
    Description = "Bucket for storing S3 access logs"
  }
}

# Enable versioning for access logs (Security requirement)
resource "aws_s3_bucket_versioning" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption for access logs (Security requirement)
resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
    bucket_key_enabled = true
  }
}

# Enable access logging on access logs bucket (Self-logging)
resource "aws_s3_bucket_logging" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "access-logs-logs/"
}

# Block public access on logs bucket
resource "aws_s3_bucket_public_access_block" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
