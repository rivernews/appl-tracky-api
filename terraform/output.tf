output "domain_name" {
  value = "https://${aws_route53_record.myapp.name}"
}

output "fully_qualified_domain_name" {
  value = "https://${aws_route53_record.myapp.fqdn}"
}