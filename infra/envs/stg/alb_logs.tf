resource "aws_s3_bucket" "alb_logs" {
  bucket        = var.alb_log_bucket_name
  force_destroy = true # Allow destruction for staging
  tags          = var.tags
}

resource "aws_s3_bucket_public_access_block" "alb_logs_block" {
  bucket = aws_s3_bucket.alb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "alb_logs_versioning" {
  bucket = aws_s3_bucket.alb_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs_sse" {
  bucket = aws_s3_bucket.alb_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs_lifecycle" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "delete_old_logs"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = 90 # 90 days for staging
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

// Allow the ELB/ALB logging service principal to write logs into the bucket.
// For us-east-1 the AWS ELB logging account ID is 127311923021. If you use a
// different region, replace the principal with the account ID for that region.
resource "aws_s3_bucket_policy" "alb_logs_policy" {
  bucket = aws_s3_bucket.alb_logs.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AWSLogDeliveryWrite",
        Effect    = "Allow",
        Principal = { AWS = "arn:aws:iam::127311923021:root" },
        Action    = "s3:PutObject",
        Resource  = "${aws_s3_bucket.alb_logs.arn}/*"
      },
      {
        Sid       = "AWSLogDeliveryAclCheck",
        Effect    = "Allow",
        Principal = { AWS = "arn:aws:iam::127311923021:root" },
        Action    = "s3:PutObjectAcl",
        Resource  = "${aws_s3_bucket.alb_logs.arn}/*"
      }
    ]
  })
}
