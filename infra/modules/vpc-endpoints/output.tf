output "vpc_endpoint_security_group_id" {
  description = "ID of the security group for VPC endpoints"
  value       = aws_security_group.vpc_endpoints.id
}

output "ecr_api_endpoint_id" {
  description = "ID of the ECR API VPC endpoint"
  value       = aws_vpc_endpoint.ecr_api.id
}

output "ecr_dkr_endpoint_id" {
  description = "ID of the ECR DKR VPC endpoint"
  value       = aws_vpc_endpoint.ecr_dkr.id
}

output "s3_endpoint_id" {
  description = "ID of the S3 VPC endpoint"
  value       = aws_vpc_endpoint.s3.id
}

output "cloudwatch_logs_endpoint_id" {
  description = "ID of the CloudWatch Logs VPC endpoint"
  value       = aws_vpc_endpoint.cloudwatch_logs.id
}

output "secrets_manager_endpoint_id" {
  description = "ID of the Secrets Manager VPC endpoint"
  value       = aws_vpc_endpoint.secrets_manager.id
}

output "rds_endpoint_id" {
  description = "ID of the RDS VPC endpoint"
  value       = aws_vpc_endpoint.rds.id
}

output "eks_endpoint_id" {
  description = "ID of the EKS VPC endpoint"
  value       = aws_vpc_endpoint.eks.id
}


