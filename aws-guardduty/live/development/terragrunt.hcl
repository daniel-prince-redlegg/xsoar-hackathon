locals {
    common_vars = yamldecode(file("variables.yml"))
}

generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
provider "aws" {
region = "${local.common_vars.aws_region}"
}
EOF
}

remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "${local.common_vars.account_name}.tf.${local.common_vars.environment}.state"

    key = "${local.common_vars.aws_region}/${local.common_vars.app_name}.tfstate"
    region         = "${local.common_vars.aws_region}"
    encrypt        = true
    dynamodb_table = "tf-lock-table"
  }
}

terraform {
  source = "../../app/"
}

inputs = {
    instance_count = 3
    instance_type = "t2.micro"
    account_name = "${local.common_vars.account_name}"
    access_key = "${local.common_vars.access_key}"
}