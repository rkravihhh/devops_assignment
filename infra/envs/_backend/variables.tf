variable "bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for state"
}

variable "region" {
  type        = string
  description = "AWS region for backend"
  default     = "us-east-1"
}

variable "tags" {
  type        = map(string)
  description = "Default tags for all resources"
  default = {
    ManagedBy = "Terraform"
    Purpose   = "RemoteState"
  }
}
