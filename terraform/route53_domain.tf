# You will also want to add a domain name, so that as your infra changes, 
# and if you rebuild your ALB, the name of your application doesn't vary. 
# Route53 will adjust as terraform changes are applied. Pretty cool.

data "aws_route53_zone" "selected" {
  name         = "shaungc.com."
  private_zone = false
}

# https://www.terraform.io/docs/providers/aws/r/route53_record.html
resource "aws_route53_record" "myapp" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "${var.project_safe_name}-api-https.shaungc.com"
  type    = "A"

  #   records = ["${aws_alb.main.public_ip}"]
  #   records = ["${aws_alb.main.dns_name}"]

  alias {
    name                   = "${aws_alb.main.dns_name}"
    zone_id                = "${aws_alb.main.zone_id}"
    evaluate_target_health = false
  }
  depends_on = ["aws_alb.main"]
}

# https://www.terraform.io/docs/providers/aws/d/acm_certificate.html
data "aws_acm_certificate" "all_shaungc" {
  domain   = "*.shaungc.com"
  statuses = ["ISSUED"]
  types       = ["AMAZON_ISSUED"]
}