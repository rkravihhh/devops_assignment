region              = "us-east-1"
aws_profile         = "default"                                         # Local AWS CLI profile (optional)
enable_assume_role  = false                                             # true in CI/CD, false for local
deployment_role_arn = "arn:aws:iam::492390865085:role/prod-deploy-role" # (only if enable_assume_role=true)

env                   = "dev"           # or "prod" / "stg"
vpc_cidr              = "172.16.0.0/16" # Updated to match architecture diagram
azs                   = ["us-east-1a", "us-east-1b"]
flow_log_iam_role_arn = "arn:aws:iam::492390865085:role/flow-log-role"

tags = {
  Owner       = "DevOps"
  Environment = "dev"
  Project     = "Fintech"
}

# -------- EKS Configuration ----------
cluster_name               = "eks-cluster"
kubernetes_version         = "1.28"
eks_endpoint_public_access = true
eks_public_access_cidrs    = ["0.0.0.0/0"]
eks_instance_types         = ["t3.medium"]
eks_desired_size           = 2
eks_max_size               = 4
eks_min_size               = 1

# -------- ALB Configuration ----------
alb_name               = "alb"
enable_https           = false
enable_alb_access_logs = true
alb_log_bucket_name    = "alb-logs-fintech-dev"


# -------- Secrets Manager Configuration ----------
secrets_manager_create_iam_policy         = true
secrets_manager_create_iam_role           = false
secrets_manager_oidc_provider_arn         = ""
secrets_manager_service_account_namespace = "default"
secrets_manager_service_account_name      = "secrets-manager-sa"

# -------- ECR Configuration ----------
ecr_repository_name          = "app"
ecr_image_tag_mutability     = "MUTABLE"
ecr_scan_on_push             = true
ecr_encryption_type          = "AES256"
ecr_enable_lifecycle_policy  = true
ecr_max_image_count          = 10
ecr_untagged_image_days      = 7
ecr_enable_repository_policy = false

# -------- DNS Configuration ----------
acm_certificate_arn   = "arn:aws:acm:us-east-1:492390865085:certificate/93ad983f-7448-4912-b6d5-fb52f05f5039"
route53_zone_id       = "Z01537862A0ATAT2PBL3Z"
route53_zone_name     = "ravihhh.shop"
create_route53_record = true
route53_record_name   = "api.dev.ravihhh.shop"
