# File: modules/vpc/variables.tf
variable "region" {
  description = "AWS region"
  type        = string
}

variable "env" {
  description = "Environment name (e.g., dev, stg, prod)"
  type        = string
}

variable "cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "azs" {
  description = "List of Availability Zones"
  type        = list(string)
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days (PCI requires >= 365)"
  type        = number
  default     = 365
}

variable "flow_log_iam_role_arn" {
  description = "IAM Role ARN for VPC Flow Logs to publish to CloudWatch"
  type        = string
  validation {
    condition = length(regexall("^arn:(aws|aws-cn|aws-us-gov):iam::\\d{12}:role/.+$", var.flow_log_iam_role_arn)) > 0
    error_message = "flow_log_iam_role_arn must be a valid IAM Role ARN (example: arn:aws:iam::123456789012:role/vpc-flow-logs-role). Replace any placeholders like [PROD_ACCOUNT_ID] with your 12-digit account id."
  }
}

variable "tags" {
  description = "A map of tags to assign to resources"
  type        = map(string)
  default     = {}
}