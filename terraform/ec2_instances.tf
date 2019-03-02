#
# the ECS optimized AMI's change by region. You can lookup the AMI here:
# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html
#
# us-east-1 ami-aff65ad2
# us-east-2 ami-64300001
# us-west-1 ami-69677709
# us-west-2 ami-40ddb938
#

#
# need to add security group config
# so that we can ssh into an ecs host from bastion box
#

resource "aws_launch_configuration" "ecs-launch-configuration" {
  name                 = "${var.project_name}-ecs-launch-config"
  image_id             = "ami-04b61a4d3b11cc8ea"
  instance_type        = "t2.micro"
  iam_instance_profile = "${aws_iam_instance_profile.ecs-instance-profile.id}"

  root_block_device {
    volume_type           = "gp2" # or "standard"
    volume_size           = 22    # GB, default in aws wizard
    delete_on_termination = true
  }

  lifecycle {
    create_before_destroy = true
  }

  associate_public_ip_address = true
  key_name                    = "${var.ec2_keypair_name}"

  # associate appropriate security group
  security_groups = ["${aws_security_group.behind_alb_sg.id}"]

  #
  # register the cluster name with ecs-agent which will in turn coord
  # with the AWS api about the cluster
  # fix refer to: https://github.com/hashicorp/terraform/issues/5660
  #
  # user_data = <> /etc/ecs/ecs.config
  # EOF

  user_data = <<EOF
    #!/bin/bash
    echo ECS_CLUSTER=${aws_ecs_cluster.test-ecs-cluster.name} >> /etc/ecs/ecs.config
    EOF
}


#
# need an ASG so we can easily add more ecs host nodes as necessary
#
resource "aws_autoscaling_group" "ecs-autoscaling-group" {
  name             = "${var.project_name}-ecs-autoscaling-group"
  max_size         = "2"
  min_size         = "1"
  desired_capacity = "1"

  vpc_zone_identifier = ["${data.aws_subnet_ids.vpc.ids}"] # when say vpc id, it's really talking about subnet

  #   vpc_zone_identifier  = ["${module.new-vpc.private_subnets}"]
  launch_configuration = "${aws_launch_configuration.ecs-launch-configuration.name}"
  health_check_type    = "ELB"
  
  # Let auto scaling group (dynamic ec2 instances) use alb's target group
  # however, this is unecessary cuz ecs service already points to alb's target group.
  # target_group_arns = ["${aws_alb_target_group.http.arn}"]

  tag {
    key                 = "Name"
    value               = "${var.project_name}-ECS-myecscluster"
    propagate_at_launch = true
  }
}

resource "aws_ecs_cluster" "test-ecs-cluster" {
  name = "${var.project_name}-ecscluster"
}


# resource "aws_alb_target_group_attachment" "test" {
#   target_group_arn = "${aws_alb_target_group.test.arn}"
#   port             = 80
#   target_id        = "${aws_instance.inst1.id}"
# }

# https://www.terraform.io/docs/providers/aws/r/security_group.html
resource "aws_security_group" "behind_alb_sg" {
  name        = "${var.project_name}_ec2_behind_alb"
  description = "Protect EC2 instances from public traffic and set them behind Application Load Balancer."
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port = 0
    to_port     = 0
    protocol    = "-1"
    security_groups = ["${aws_security_group.public_alb.id}"] // only from alb
  }

  # allow all traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
