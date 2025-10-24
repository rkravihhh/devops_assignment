output "bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.tfstate.bucket
}

output "prod_bucket_name" {
  description = "Production S3 bucket name"
  value       = aws_s3_bucket.tfstate_prod.bucket
}

output "stg_bucket_name" {
  description = "Staging S3 bucket name"
  value       = aws_s3_bucket.tfstate_stg.bucket
}

output "kms_key_arn" {
  description = "KMS key ARN"
  value       = aws_kms_key.tf_kms.arn
}
