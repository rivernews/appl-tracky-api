# https://www.terraform.io/docs/providers/aws/d/subnet_ids.html
data "aws_subnet_ids" "vpc" {
  vpc_id = "${var.vpc_id}"

  # export:
  # ids
}
