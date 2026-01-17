resource "aws_route53_zone" "main" {
  name = var.domain_name
}

resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = ["placeholder-aptible-endpoint"]
}

resource "aws_route53_record" "web" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"
  # Alias to CloudFront or Aptible if using Apex
  # For now, CNAME if using www or placeholder
  alias {
    name                   = "placeholder-frontend-endpoint"
    zone_id                = "Z2FDTNDATAQYW2" # CloudFront Zone ID example
    evaluate_target_health = false
  }
}
