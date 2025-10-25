variable "env" {
  description = "Environment name"
  type        = string
}

variable "secrets" {
  description = "Map of secrets to create"
  type = map(object({
    description             = string
    purpose                = string
    password_length        = number
    special_characters     = bool
    upper_case            = bool
    lower_case            = bool
    numeric               = bool
    recovery_window_in_days = number
    kms_key_id            = string
    additional_fields     = map(string)
  }))
  default = {}
}

variable "create_iam_policy" {
  description = "Create IAM policy for secrets access"
  type        = bool
  default     = true
}

variable "create_iam_role" {
  description = "Create IAM role for EKS service account"
  type        = bool
  default     = false
}

variable "oidc_provider_arn" {
  description = "OIDC provider ARN for EKS service account"
  type        = string
  default     = ""
}

variable "service_account_namespace" {
  description = "Kubernetes namespace for service account"
  type        = string
  default     = "default"
}

variable "service_account_name" {
  description = "Kubernetes service account name"
  type        = string
  default     = "secrets-manager-sa"
}

variable "tags" {
  description = "A map of tags to assign to the resource"
  type        = map(string)
  default     = {}
}
