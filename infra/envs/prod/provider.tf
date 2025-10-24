terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.region
  profile = var.aws_profile # for local 
  dynamic "assume_role" {
    for_each = var.enable_assume_role ? [1] : []
    content {
      role_arn = var.deployment_role_arn
    }
  }
}
