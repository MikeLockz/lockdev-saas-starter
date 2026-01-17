resource "aws_cloudwatch_log_group" "api" {
  name              = "/aptible/lockdev-api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/aptible/lockdev-worker"
  retention_in_days = 30
}

resource "aws_iam_user" "log_drain" {
  name = "aptible-log-drain"
}

resource "aws_iam_access_key" "log_drain" {
  user = aws_iam_user.log_drain.name
}

resource "aws_iam_user_policy" "log_drain" {
  name = "aptible-log-drain-policy"
  user = aws_iam_user.log_drain.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

output "cloudwatch_log_drain_access_key_id" {
  value = aws_iam_access_key.log_drain.id
}

output "cloudwatch_log_drain_secret_key" {
  value     = aws_iam_access_key.log_drain.secret
  sensitive = true
}
