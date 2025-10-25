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

# Common
variable "tags" {
  description = "Map of tags applied to resources"
  type        = map(string)
  default     = {}
}