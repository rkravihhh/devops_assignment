terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
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
  source                  = "../../modules/vpc-endpoints"
  env                     = var.env
  region                  = var.region
  vpc_id                  = module.vpc.vpc_id
  vpc_cidr                = module.vpc.vpc_cidr_block
  private_subnet_ids      = module.vpc.private_subnet_ids
  private_route_table_ids = module.vpc.private_route_table_ids
  tags                    = var.tags
}

# EKS Cluster
module "eks" {
  source                 = "../../modules/eks"
  env                    = var.env
  cluster_name           = var.cluster_name
  kubernetes_version     = var.kubernetes_version
  subnet_ids             = concat(module.vpc.public_subnet_ids, module.vpc.private_subnet_ids)
  private_subnet_ids     = module.vpc.private_subnet_ids
  endpoint_public_access = var.eks_endpoint_public_access
  public_access_cidrs    = var.eks_public_access_cidrs
  instance_types         = var.eks_instance_types
  desired_size           = var.eks_desired_size
  max_size               = var.eks_max_size
  min_size               = var.eks_min_size
  tags                   = var.tags
}

# ECR Repository for Docker Images
module "ecr" {
  source                   = "../../modules/ecr"
  repository_name          = "${var.env}-${var.ecr_repository_name}"
  image_tag_mutability     = var.ecr_image_tag_mutability
  scan_on_push             = var.ecr_scan_on_push
  encryption_type          = var.ecr_encryption_type
  enable_lifecycle_policy  = var.ecr_enable_lifecycle_policy
  max_image_count          = var.ecr_max_image_count
  untagged_image_days      = var.ecr_untagged_image_days
  enable_repository_policy = var.ecr_enable_repository_policy
  allowed_principals       = var.ecr_allowed_principals
  tags                     = var.tags
}


# Secrets Manager for secure secret storage
module "secrets_manager" {
  source                    = "../../modules/secrets-manager"
  env                       = var.env
  secrets                   = var.secrets_manager_secrets
  create_iam_policy         = var.secrets_manager_create_iam_policy
  create_iam_role           = var.secrets_manager_create_iam_role
  oidc_provider_arn         = var.secrets_manager_oidc_provider_arn
  service_account_namespace = var.secrets_manager_service_account_namespace
  service_account_name      = var.secrets_manager_service_account_name
  tags                      = var.tags
}


# Application Load Balancer for Ingress
module "alb" {
  source                = "../../modules/alb"
  env                   = var.env
  alb_name              = var.alb_name
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.public_subnet_ids
  enable_https          = var.enable_https
  certificate_arn       = var.acm_certificate_arn
  enable_access_logs    = var.enable_alb_access_logs
  access_logs_bucket    = var.alb_log_bucket_name
  access_logs_prefix    = "${var.env}/alb"
  create_route53_record = var.create_route53_record
  route53_zone_id       = var.route53_zone_id
  route53_record_name   = var.route53_record_name
  tags                  = var.tags
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

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "ecr_repository_arn" {
  description = "The ARN of the ECR repository"
  value       = module.ecr.repository_arn
}


output "secrets_manager_secret_arns" {
  description = "ARNs of the created secrets"
  value       = module.secrets_manager.secret_arns
}

output "secrets_manager_iam_policy_arn" {
  description = "ARN of the IAM policy for secrets access"
  value       = module.secrets_manager.iam_policy_arn
}

output "secrets_manager_iam_role_arn" {
  description = "ARN of the IAM role for EKS service account"
  value       = module.secrets_manager.iam_role_arn
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = module.eks.cluster_arn
}

output "eks_cluster_certificate_authority_data" {
  description = "Base64 encoded certificate authority data for the EKS cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "eks_cluster_oidc_issuer_url" {
  description = "OIDC issuer URL for the EKS cluster"
  value       = module.eks.cluster_oidc_issuer_url
}

