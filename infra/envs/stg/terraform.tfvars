region               = "us-east-1"
aws_profile          = "default"                # Local AWS CLI profile (optional)
enable_assume_role   = true                     # true in CI/CD, false for local
deployment_role_arn  = "arn:aws:iam::492390865085:role/stg-deploy-role" # (only if enable_assume_role=true)

env                  = "stg"                    # or "prod" / "stg"
vpc_cidr             = "172.16.0.0/16"          # Updated to match architecture diagram
azs                  = ["us-east-1a", "us-east-1b"]
flow_log_iam_role_arn= "arn:aws:iam::492390865085:role/flow-log-role"

tags = {
  Owner       = "DevOps"
  Environment = "stg"
  Project     = "Fintech"
  Criticality = "Medium"
}

# -------- EKS Configuration ----------
cluster_name         = "eks-cluster"
kubernetes_version   = "1.28"
eks_endpoint_public_access = true
eks_public_access_cidrs = ["0.0.0.0/0"]
eks_instance_types   = ["t3.medium"]
eks_desired_size     = 2
eks_max_size         = 4
eks_min_size         = 1

# -------- ALB Configuration ----------
alb_name             = "alb"
enable_https         = true
enable_alb_access_logs = true
alb_log_bucket_name  = "alb-logs-fintech-stg"

# -------- DNS Configuration ----------
acm_certificate_arn  = "arn:aws:acm:us-east-1:492390865085:certificate/xxxxxxxx-xxxx-xxxx"
route53_zone_id      = "Z12345678ABCDEFG"
route53_zone_name    = "staging.example.com"
create_route53_record = true
route53_record_name  = "api.stg.example.com"
