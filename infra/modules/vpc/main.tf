# File: modules/vpc/main.tf
provider "aws" {
  region = var.region
}

resource "aws_vpc" "main" {
  cidr_block           = var.cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(var.tags, {
    Name = "${var.env}-vpc"
  })
}

# --- Subnets ---
resource "aws_subnet" "public" {
  count                   = length(var.azs)
  vpc_id                  = aws_vpc.main.id
  availability_zone       = var.azs[count.index]
  cidr_block              = cidrsubnet(var.cidr, 8, count.index)
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name   = "${var.env}-public-subnet-${count.index + 1}"
    "kubernetes.io/role/elb" = "1" # For AWS LBC
  })
}

resource "aws_subnet" "private" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  availability_zone = var.azs[count.index]
  cidr_block        = cidrsubnet(var.cidr, 8, length(var.azs) + count.index)

  tags = merge(var.tags, {
    Name   = "${var.env}-private-subnet-${count.index + 1}"
    "kubernetes.io/role/internal-elb" = "1" # For internal services
  })
}

# --- Routing ---
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = merge(var.tags, {
    Name = "${var.env}-igw"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.env}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  count          = length(var.azs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# --- NAT Gateway for Private Subnets ---
resource "aws_eip" "nat" {
  count = length(var.azs)
  domain   = "vpc"
  tags = merge(var.tags, {
    Name = "${var.env}-nat-eip-${count.index + 1}"
  })
}

resource "aws_nat_gateway" "main" {
  count         = length(var.azs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.tags, {
    Name = "${var.env}-nat-gw-${count.index + 1}"
  })
}

resource "aws_route_table" "private" {
  count  = length(var.azs)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(var.tags, {
    Name = "${var.env}-private-rt-${count.index + 1}"
  })
}

resource "aws_route_table_association" "private" {
  count          = length(var.azs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# --- PCI Requirement: VPC Flow Logs ---
resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "/aws/vpc-flow-logs/${var.env}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

resource "aws_flow_log" "main" {
  iam_role_arn    = var.flow_log_iam_role_arn # Assumes role is created elsewhere
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  # This is a critical assumption - you need an IAM role for flow logs
  # See "Open Questions" in ARCHITECTURE.md
}