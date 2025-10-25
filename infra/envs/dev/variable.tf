variable "region" {}
variable "env" {}
variable "aws_profile" {
  default     = null
  description = "AWS CLI profile for local"
}
variable "enable_assume_role" {
  default     = false
  description = "Enable role assumption for CI/CD"
}
variable "deployment_role_arn" {
  default     = null
  description = "AssumeRole ARN for CI/CD deploy"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "172.16.0.0/16"
}

variable "azs" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "flow_log_iam_role_arn" {
  description = "IAM role ARN used for VPC flow logs"
  default     = null
}

# EKS Configuration
variable "cluster_name" {
  description = "Name of the EKS cluster"
  default     = "eks-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  default     = "1.28"
}

variable "eks_endpoint_public_access" {
  description = "Whether the Amazon EKS public API server endpoint is enabled"
  type        = bool
  default     = true
}

variable "eks_public_access_cidrs" {
  description = "List of CIDR blocks which can access the Amazon EKS public API server endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "eks_instance_types" {
  description = "List of instance types for the EKS node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "eks_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 4
}

variable "eks_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

# ALB Configuration
variable "alb_name" {
  description = "Name of the Application Load Balancer"
  default     = "alb"
}

variable "enable_https" {
  description = "Enable HTTPS listener"
  type        = bool
  default     = true
}

variable "enable_alb_access_logs" {
  description = "Enable ALB access logs"
  type        = bool
  default     = true
}

variable "alb_log_bucket_name" {
  description = "S3 bucket name used for ALB access logs"
}

# DNS Configuration
variable "acm_certificate_arn" {
  description = "ACM certificate ARN for the application/load balancer"
  default     = null
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for DNS records"
  default     = null
}

variable "route53_zone_name" {
  description = "Route53 hosted zone name (e.g. example.com)"
  default     = null
}

variable "create_route53_record" {
  description = "Create Route53 record"
  type        = bool
  default     = false
}

variable "route53_record_name" {
  description = "Route53 record name"
  default     = null
}



# Secrets Manager Configuration
variable "secrets_manager_secrets" {
  description = "Map of secrets to create in Secrets Manager"
  type = map(object({
    description             = string
    purpose                 = string
    password_length         = number
    special_characters      = bool
    upper_case              = bool
    lower_case              = bool
    numeric                 = bool
    recovery_window_in_days = number
    kms_key_id              = string
    additional_fields       = map(string)
  }))
  default = {
    "api-key-v3" = {
      description             = "API key for external services"
      purpose                 = "API Integration"
      password_length         = 32
      special_characters      = true
      upper_case              = true
      lower_case              = true
      numeric                 = true
      recovery_window_in_days = 7
      kms_key_id              = null
      additional_fields = {
        service     = "external-api"
        environment = "dev"
      }
    }
    "jwt-secret-v3" = {
      description             = "JWT signing secret"
      purpose                 = "Authentication"
      password_length         = 64
      special_characters      = true
      upper_case              = true
      lower_case              = true
      numeric                 = true
      recovery_window_in_days = 7
      kms_key_id              = null
      additional_fields = {
        algorithm  = "HS256"
        expires_in = "24h"
      }
    }
  }
}

variable "secrets_manager_create_iam_policy" {
  description = "Create IAM policy for secrets access"
  type        = bool
  default     = true
}

variable "secrets_manager_create_iam_role" {
  description = "Create IAM role for EKS service account"
  type        = bool
  default     = false
}

variable "secrets_manager_oidc_provider_arn" {
  description = "OIDC provider ARN for EKS service account"
  type        = string
  default     = ""
}

variable "secrets_manager_service_account_namespace" {
  description = "Kubernetes namespace for service account"
  type        = string
  default     = "default"
}

variable "secrets_manager_service_account_name" {
  description = "Kubernetes service account name"
  type        = string
  default     = "secrets-manager-sa"
}

# ECR Configuration
variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  default     = "app"
}

variable "ecr_image_tag_mutability" {
  description = "The tag mutability setting for the repository"
  type        = string
  default     = "MUTABLE"
}

variable "ecr_scan_on_push" {
  description = "Indicates whether images are scanned after being pushed to the repository"
  type        = bool
  default     = true
}

variable "ecr_encryption_type" {
  description = "The encryption type to use for the repository"
  type        = string
  default     = "AES256"
}

variable "ecr_enable_lifecycle_policy" {
  description = "Enable lifecycle policy for the repository"
  type        = bool
  default     = true
}

variable "ecr_max_image_count" {
  description = "Maximum number of images to keep"
  type        = number
  default     = 10
}

variable "ecr_untagged_image_days" {
  description = "Number of days to keep untagged images"
  type        = number
  default     = 7
}

variable "ecr_enable_repository_policy" {
  description = "Enable repository policy"
  type        = bool
  default     = false
}

variable "ecr_allowed_principals" {
  description = "List of AWS principals allowed to pull images"
  type        = list(string)
  default     = []
}

# Common
variable "tags" {
  description = "Map of tags applied to resources"
  type        = map(string)
  default     = {}
}

