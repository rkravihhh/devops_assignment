terraform {
  backend "s3" {
    bucket         = "fintech-tfstate-dev"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    use_lockfile   = true
  }
}
