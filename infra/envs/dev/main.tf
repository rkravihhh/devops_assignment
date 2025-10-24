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

# Networking
module "vpc" {
  source                = "../../modules/vpc"
  region                = var.region
  env                   = var.env
  cidr                  = var.vpc_cidr
  azs                   = var.azs
  flow_log_iam_role_arn = var.flow_log_iam_role_arn
  tags                  = var.tags
}

# VPC Endpoints for secure AWS service access
module "vpc_endpoints" {
  source                 = "../../modules/vpc-endpoints"
  env                    = var.env
  region                 = var.region
  vpc_id                 = module.vpc.vpc_id
  vpc_cidr               = module.vpc.vpc_cidr_block
  private_subnet_ids     = module.vpc.private_subnet_ids
  private_route_table_ids = module.vpc.private_route_table_ids
  tags                   = var.tags
}

# EKS Cluster
module "eks" {
  source              = "../../modules/eks"
  env                 = var.env
  cluster_name        = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  subnet_ids          = concat(module.vpc.public_subnet_ids, module.vpc.private_subnet_ids)
  private_subnet_ids  = module.vpc.private_subnet_ids
  endpoint_public_access = var.eks_endpoint_public_access
  public_access_cidrs = var.eks_public_access_cidrs
  instance_types      = var.eks_instance_types
  desired_size        = var.eks_desired_size
  max_size           = var.eks_max_size
  min_size           = var.eks_min_size
  tags               = var.tags
}

# Application Load Balancer for Ingress
module "alb" {
  source                    = "../../modules/alb"
  env                       = var.env
  alb_name                  = var.alb_name
  vpc_id                    = module.vpc.vpc_id
  subnet_ids                = module.vpc.public_subnet_ids
  enable_https              = var.enable_https
  certificate_arn           = var.acm_certificate_arn
  enable_access_logs        = var.enable_alb_access_logs
  access_logs_bucket        = var.alb_log_bucket_name
  access_logs_prefix        = "${var.env}/alb"
  create_route53_record    = var.create_route53_record
  route53_zone_id          = var.route53_zone_id
  route53_record_name       = var.route53_record_name
  tags                      = var.tags
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS Kubernetes API server"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "application_url" {
  description = "The URL for the deployed application"
  value       = var.create_route53_record ? "https://${var.route53_record_name}" : "https://${module.alb.alb_dns_name}"
}
