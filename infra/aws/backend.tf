# Backend configuration for state storage
# Note: This file should be uncommented after the S3 bucket and DynamoDB table are created
# Initial setup requires local state, then migrate to S3 backend

terraform {
  backend "s3" {
    bucket         = "boundaryhealth-terraform-state"
    key            = "aws/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "boundaryhealth-terraform-lock"
  }
}

# S3 bucket for state storage
resource "aws_s3_bucket" "terraform_state" {
  # checkov:skip=CKV_AWS_144:Cross-region replication not required for starter kit
  # checkov:skip=CKV2_AWS_61:Lifecycle configuration not required for terraform state bucket
  # checkov:skip=CKV2_AWS_62:Event notifications not required for terraform state bucket
  # checkov:skip=CKV_AWS_145:Using KMS encryption via server_side_encryption_configuration
  # checkov:skip=CKV_AWS_18:Logging enabled via separate aws_s3_bucket_logging resource
  bucket = var.state_bucket_name

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State Storage"
    Description = "S3 bucket for storing Terraform state files"
  }
}

# Enable versioning for state history
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}

# Enable logging for state bucket
resource "aws_s3_bucket_logging" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "tf-state-logs/"
}

# Block public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_lock" {
  # checkov:skip=CKV_AWS_119:Using KMS CMK via server_side_encryption block
  name         = var.state_dynamodb_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  # Enable server-side encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.main.arn
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State Lock"
    Description = "DynamoDB table for Terraform state locking"
  }
}