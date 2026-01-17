resource "aws_secretsmanager_secret" "gcp_credentials" {
  name_prefix = "lockdev-gcp-credentials-"
}
