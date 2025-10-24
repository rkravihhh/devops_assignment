terraform {
  backend "s3" {
    bucket         = "fintech-tfstate-stg"
    key            = "stg/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    use_lockfile   = true
  }
}
