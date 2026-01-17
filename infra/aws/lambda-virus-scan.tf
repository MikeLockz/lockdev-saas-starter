resource "aws_s3_bucket" "quarantine" {
  bucket_prefix = "lockdev-quarantine-"
}

resource "aws_iam_role" "virus_scan_lambda" {
  name = "virus-scan-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_lambda_function" "virus_scan" {
  filename      = "virus_scan.zip" # Placeholder
  function_name = "virus-scan"
  role          = aws_iam_role.virus_scan_lambda.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.virus_scan.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.app_storage.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.app_storage.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.virus_scan.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
