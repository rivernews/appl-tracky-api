output "domain_name" {
  value = "https://${aws_route53_record.myapp.name}"
}

output "fully_qualified_domain_name" {
  value = "https://${aws_route53_record.myapp.fqdn}"
}

output "ecr_new_image_tag" {
  value = "${var.ecr_new_image_tag}"
}