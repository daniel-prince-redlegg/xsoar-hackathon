variable "account_name" {}
variable "access_key" {}

data "aws_vpc" "tower-vpc" {
  tags = {"Name": "aws-controltower-VPC"}
}

data "aws_subnet_ids" "all" {
  vpc_id = data.aws_vpc.tower-vpc.id
}

resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow http inbound traffic"
  vpc_id      = data.aws_vpc.tower-vpc.id

  ingress {
    description = "http from VPC"
    to_port     = 80
    from_port = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "template_file" "user_data" {
  template = file("user_data.tpl")

  vars = {
    account_name = var.account_name
  }
}

resource "aws_launch_configuration" "web_conf" {
  name = "web_config"
  image_id = "ami-0603cbe34fd08cb81"
  instance_type = "t2.micro"
  key_name = var.access_key
  security_groups = [aws_security_group.allow_http.id]
  iam_instance_profile = "AmazonSSMRoleForInstancesQuickSetup"

  user_data = data.template_file.user_data.rendered
}


resource "aws_autoscaling_group" "web" {
  name                 = "web-asg"
  launch_configuration = aws_launch_configuration.web_conf.name
  min_size             = 2
  max_size             = 3
  vpc_zone_identifier = data.aws_subnet_ids.all.ids
  target_group_arns = [aws_lb_target_group.tg.arn]
}

resource "aws_lb_target_group" "tg" {
  name     = "lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.tower-vpc.id
}

resource "aws_lb" "weblb" {
  name = "weblb"
  internal = false
  load_balancer_type = "application"
  subnets = data.aws_subnet_ids.all.ids
  enable_deletion_protection = false
  security_groups = [aws_security_group.allow_http.id]
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.weblb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}


output "webserver" {
  value = aws_lb.weblb.dns_name
}





