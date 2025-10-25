# AWS Secrets Manager Module
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Random password generator
resource "random_password" "passwords" {
  for_each = var.secrets

  length  = each.value.password_length
  special = each.value.special_characters
  upper   = each.value.upper_case
  lower   = each.value.lower_case
  numeric = each.value.numeric
}

# Secrets Manager secrets
resource "aws_secretsmanager_secret" "secrets" {
  for_each = var.secrets

  name                    = "${var.env}-${each.key}"
  description             = each.value.description
  recovery_window_in_days  = each.value.recovery_window_in_days
  kms_key_id             = each.value.kms_key_id

  tags = merge(var.tags, {
    Name        = "${var.env}-${each.key}"
    Environment = var.env
    Purpose     = each.value.purpose
  })
}

# Secret versions
resource "aws_secretsmanager_secret_version" "secrets" {
  for_each = var.secrets

  secret_id = aws_secretsmanager_secret.secrets[each.key].id
  secret_string = jsonencode(merge(
    {
      password = random_password.passwords[each.key].result
    },
    each.value.additional_fields
  ))
}

# IAM policy for EKS pods to access secrets
resource "aws_iam_policy" "secrets_access" {
  count = var.create_iam_policy ? 1 : 0

  name        = "${var.env}-secrets-access-policy"
  description = "Policy for accessing Secrets Manager secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.secrets : secret.arn
        ]
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.env}-secrets-access-policy"
  })
}

# IAM role for EKS service account
resource "aws_iam_role" "secrets_role" {
  count = var.create_iam_role ? 1 : 0

  name = "${var.env}-secrets-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(var.oidc_provider_arn, "/^.*oidc-provider\\//", "")}:sub" = "system:serviceaccount:${var.service_account_namespace}:${var.service_account_name}"
            "${replace(var.oidc_provider_arn, "/^.*oidc-provider\\//", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.env}-secrets-role"
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "secrets_policy" {
  count = var.create_iam_role ? 1 : 0

  role       = aws_iam_role.secrets_role[0].name
  policy_arn = aws_iam_policy.secrets_access[0].arn
}
