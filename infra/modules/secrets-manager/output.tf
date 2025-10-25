output "secret_arns" {
  description = "ARNs of the created secrets"
  value = {
    for k, v in aws_secretsmanager_secret.secrets : k => v.arn
  }
}

output "secret_names" {
  description = "Names of the created secrets"
  value = {
    for k, v in aws_secretsmanager_secret.secrets : k => v.name
  }
}

output "secret_versions" {
  description = "Version IDs of the created secrets"
  value = {
    for k, v in aws_secretsmanager_secret_version.secrets : k => v.version_id
  }
}

output "iam_policy_arn" {
  description = "ARN of the IAM policy for secrets access"
  value       = var.create_iam_policy ? aws_iam_policy.secrets_access[0].arn : null
}

output "iam_role_arn" {
  description = "ARN of the IAM role for EKS service account"
  value       = var.create_iam_role ? aws_iam_role.secrets_role[0].arn : null
}

output "iam_role_name" {
  description = "Name of the IAM role for EKS service account"
  value       = var.create_iam_role ? aws_iam_role.secrets_role[0].name : null
}
