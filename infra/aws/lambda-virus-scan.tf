# Quarantine bucket for infected files
resource "aws_s3_bucket" "quarantine" {
  bucket = "${var.project_name}-quarantine-${var.environment}"

  tags = {
    Name        = "Quarantine Bucket"
    Description = "S3 bucket for storing quarantined files that failed virus scan"
    Compliance  = "HIPAA"
  }
}

# Enable versioning for quarantine bucket
resource "aws_s3_bucket_versioning" "quarantine" {
  bucket = aws_s3_bucket.quarantine.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption for quarantine bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "quarantine" {
  bucket = aws_s3_bucket.quarantine.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block all public access on quarantine bucket
resource "aws_s3_bucket_public_access_block" "quarantine" {
  bucket = aws_s3_bucket.quarantine.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role for Lambda virus scanner
resource "aws_iam_role" "virus_scanner" {
  name = "${var.project_name}-virus-scanner-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "Virus Scanner Lambda Role"
  }
}

# IAM policy for Lambda to access S3 buckets
resource "aws_iam_role_policy" "virus_scanner_s3" {
  name = "s3-access"
  role = aws_iam_role.virus_scanner.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObjectTagging",
          "s3:PutObjectVersionTagging"
        ]
        Resource = "${aws_s3_bucket.documents.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectTagging"
        ]
        Resource = "${aws_s3_bucket.quarantine.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:DeleteObject",
          "s3:DeleteObjectVersion"
        ]
        Resource = "${aws_s3_bucket.documents.arn}/*"
      }
    ]
  })
}

# Attach basic Lambda execution role
resource "aws_iam_role_policy_attachment" "virus_scanner_basic" {
  role       = aws_iam_role.virus_scanner.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function for virus scanning
resource "aws_lambda_function" "virus_scanner" {
  filename      = "${path.module}/lambda-virus-scan.zip"
  function_name = "${var.project_name}-virus-scanner-${var.environment}"
  role          = aws_iam_role.virus_scanner.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 3008

  # ClamAV layer - using public layer from https://github.com/Cisco-Talos/clamav-lambda
  # Note: This ARN is region-specific and version-specific
  # For production, you should build and host your own layer
  layers = [
    # This is a placeholder - you need to either:
    # 1. Build your own ClamAV layer
    # 2. Use a third-party layer ARN for your region
    # Example: "arn:aws:lambda:us-west-2:123456789012:layer:clamav:1"
  ]

  environment {
    variables = {
      QUARANTINE_BUCKET = aws_s3_bucket.quarantine.id
      SOURCE_BUCKET     = aws_s3_bucket.documents.id
    }
  }

  tags = {
    Name = "Virus Scanner Lambda"
  }

  # Placeholder for the actual Lambda code
  # The lambda-virus-scan.zip should be created separately
  source_code_hash = fileexists("${path.module}/lambda-virus-scan.zip") ? filebase64sha256("${path.module}/lambda-virus-scan.zip") : null

  lifecycle {
    ignore_changes = [
      source_code_hash,
      filename
    ]
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "virus_scanner" {
  name              = "/aws/lambda/${aws_lambda_function.virus_scanner.function_name}"
  retention_in_days = 30

  tags = {
    Name = "Virus Scanner Logs"
  }
}

# Lambda permission for S3 to invoke the function
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.virus_scanner.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.documents.arn
}

# S3 bucket notification to trigger Lambda on object creation
resource "aws_s3_bucket_notification" "documents_virus_scan" {
  bucket = aws_s3_bucket.documents.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.virus_scanner.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ""
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
