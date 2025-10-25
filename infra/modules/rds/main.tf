# RDS Database Module
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Random password for database
resource "random_password" "master_password" {
  length  = 16
  special = true
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.env}-${var.db_identifier}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = merge(var.tags, {
    Name = "${var.env}-${var.db_identifier}-subnet-group"
  })
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "${var.env}-${var.db_identifier}-sg"
  description = "Security group for RDS database"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.env}-${var.db_identifier}-sg"
  })
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.env}-${var.db_identifier}"

  # Engine configuration
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.instance_class

  # Storage configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = var.storage_encrypted

  # Database configuration
  db_name  = var.db_name
  username = var.username
  password = var.password != null ? var.password : random_password.master_password.result

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = var.publicly_accessible

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window

  # Monitoring
  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn

  # Performance Insights
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period

  # Deletion protection
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot
  final_snapshot_identifier = var.final_snapshot_identifier

  # Multi-AZ
  multi_az = var.multi_az

  # Parameter group
  parameter_group_name = var.parameter_group_name

  # Option group
  option_group_name = var.option_group_name

  tags = merge(var.tags, {
    Name = "${var.env}-${var.db_identifier}"
  })

  depends_on = [aws_db_subnet_group.main]
}

# Store password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  count = var.store_password_in_secrets_manager ? 1 : 0
  
  name                    = "${var.env}-${var.db_identifier}-password"
  description             = "Database password for ${var.env}-${var.db_identifier}"
  recovery_window_in_days = 7

  tags = merge(var.tags, {
    Name = "${var.env}-${var.db_identifier}-password"
  })
}

resource "aws_secretsmanager_secret_version" "db_password" {
  count = var.store_password_in_secrets_manager ? 1 : 0
  
  secret_id = aws_secretsmanager_secret.db_password[0].id
  secret_string = jsonencode({
    username = var.username
    password = var.password != null ? var.password : random_password.master_password.result
    engine   = var.engine
    host     = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
    dbname   = var.db_name
  })
}
