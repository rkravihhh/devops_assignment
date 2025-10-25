terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "tfstate" {
  bucket        = var.bucket_name
  force_destroy = false
  tags          = var.tags
}

# Production state bucket
resource "aws_s3_bucket" "tfstate_prod" {
  bucket        = "fintech-tfstate-prod"
  force_destroy = false
  tags          = merge(var.tags, { Environment = "prod" })
}

# Staging state bucket
resource "aws_s3_bucket" "tfstate_stg" {
  bucket        = "fintech-tfstate-stg"
  force_destroy = false
  tags          = merge(var.tags, { Environment = "stg" })
}

resource "aws_s3_bucket_versioning" "tfstate_versioning" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "tfstate_prod_versioning" {
  bucket = aws_s3_bucket.tfstate_prod.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "tfstate_stg_versioning" {
  bucket = aws_s3_bucket.tfstate_stg.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_kms_key" "tf_kms" {
  description             = "KMS key for Terraform state"
  deletion_window_in_days = 7
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate_sse" {
  bucket = aws_s3_bucket.tfstate.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.tf_kms.arn
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate_prod_sse" {
  bucket = aws_s3_bucket.tfstate_prod.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.tf_kms.arn
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate_stg_sse" {
  bucket = aws_s3_bucket.tfstate_stg.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.tf_kms.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate_block" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "tfstate_prod_block" {
  bucket                  = aws_s3_bucket.tfstate_prod.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "tfstate_stg_block" {
  bucket                  = aws_s3_bucket.tfstate_stg.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
