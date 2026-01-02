# AWS Configuration
aws_region = "us-west-2"

# Environment (dev, staging, or production)
environment = "dev"

# Project name (used for resource naming)
project_name = "lockdev-saas"

# Domain name for SES and Route53
domain_name = "boundaryhealth.app"

# S3 bucket for Terraform state
state_bucket_name = "boundaryhealth-terraform-state"

# DynamoDB table for state locking
state_dynamodb_table = "boundaryhealth-terraform-lock"

# Set to false if Route53 hosted zone already exists
enable_route53 = true
