variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "lockdev-saas"
}

variable "domain_name" {
  description = "Domain name for SES and Route53"
  type        = string
}

variable "state_bucket_name" {
  description = "S3 bucket name for Terraform state storage"
  type        = string
}

variable "state_dynamodb_table" {
  description = "DynamoDB table name for state locking"
  type        = string
  default     = "terraform-state-lock"
}

variable "enable_route53" {
  description = "Whether to create Route53 hosted zone (set to false if zone already exists)"
  type        = bool
  default     = true
}
