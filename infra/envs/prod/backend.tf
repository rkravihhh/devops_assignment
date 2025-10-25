terraform {
  backend "s3" {
    bucket  = "fintech-tfstate-prod"
    key     = "prod/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}
