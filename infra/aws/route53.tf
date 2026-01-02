# Route53 Hosted Zone
resource "aws_route53_zone" "main" {
  count = var.enable_route53 ? 1 : 0
  name  = var.domain_name

  tags = {
    Name        = "Main DNS Zone"
    Description = "Hosted zone for ${var.domain_name}"
  }
}

# Data source for existing hosted zone (if not creating new one)
data "aws_route53_zone" "main" {
  count = var.enable_route53 ? 0 : 1
  name  = var.domain_name
}

# Local value to reference the zone ID
locals {
  zone_id = var.enable_route53 ? aws_route53_zone.main[0].zone_id : data.aws_route53_zone.main[0].zone_id
}

# SES Domain Verification TXT Record
resource "aws_route53_record" "ses_verification" {
  zone_id = local.zone_id
  name    = "_amazonses.${var.domain_name}"
  type    = "TXT"
  ttl     = 600
  records = [aws_ses_domain_identity.main.verification_token]
}

# SES DKIM Records
resource "aws_route53_record" "ses_dkim" {
  count   = 3
  zone_id = local.zone_id
  name    = "${aws_ses_domain_dkim.main.dkim_tokens[count.index]}._domainkey.${var.domain_name}"
  type    = "CNAME"
  ttl     = 600
  records = ["${aws_ses_domain_dkim.main.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

# SPF Record for SES
resource "aws_route53_record" "spf" {
  zone_id = local.zone_id
  name    = var.domain_name
  type    = "TXT"
  ttl     = 600
  records = ["v=spf1 include:amazonses.com ~all"]
}

# DMARC Record
resource "aws_route53_record" "dmarc" {
  zone_id = local.zone_id
  name    = "_dmarc.${var.domain_name}"
  type    = "TXT"
  ttl     = 600
  records = ["v=DMARC1; p=quarantine; rua=mailto:dmarc@${var.domain_name}"]
}

# MX Record for receiving emails (if needed)
resource "aws_route53_record" "mx" {
  zone_id = local.zone_id
  name    = var.domain_name
  type    = "MX"
  ttl     = 600
  records = ["10 inbound-smtp.${var.aws_region}.amazonaws.com"]
}

# Example A record for API (update with actual Aptible endpoint)
# resource "aws_route53_record" "api" {
#   zone_id = local.zone_id
#   name    = "api.${var.domain_name}"
#   type    = "CNAME"
#   ttl     = 300
#   records = ["REPLACE_WITH_APTIBLE_ENDPOINT"]
# }

# Example A record for frontend (update with actual hosting endpoint)
# resource "aws_route53_record" "www" {
#   zone_id = local.zone_id
#   name    = "www.${var.domain_name}"
#   type    = "CNAME"
#   ttl     = 300
#   records = ["REPLACE_WITH_FRONTEND_ENDPOINT"]
# }
