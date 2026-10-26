# Red y seguridad. La RDS queda en subredes privadas y solo acepta
# PostgreSQL (5432) desde el security group de la instancia EC2.

data "aws_vpc" "principal" {
  id = var.vpc_id
}

resource "aws_subnet" "publica" {
  vpc_id                  = data.aws_vpc.principal.id
  cidr_block              = "172.31.10.0/24"
  availability_zone       = var.az_ec2
  map_public_ip_on_launch = true

  tags = { Name = "${var.proyecto}-publica" }
}

resource "aws_subnet" "privada_a" {
  vpc_id            = data.aws_vpc.principal.id
  cidr_block        = "172.31.20.0/24"
  availability_zone = var.az_ec2

  tags = { Name = "${var.proyecto}-privada-a" }
}

resource "aws_subnet" "privada_b" {
  vpc_id            = data.aws_vpc.principal.id
  cidr_block        = "172.31.30.0/24"
  availability_zone = var.az_rds

  tags = { Name = "${var.proyecto}-privada-b" }
}

# EC2: SSH (22), HTTP (80) y API directa (5000, solo diagnóstico tras nginx).
resource "aws_security_group" "ec2" {
  name        = "keibeauty-ec2-sg"
  description = "Tráfico frontal del backend KeiBeauty"
  vpc_id      = data.aws_vpc.principal.id

  ingress {
    description = "SSH despliegue"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP frontal (nginx)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "API directa (diagnóstico)"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "keibeauty-ec2-sg" }
}

# RDS: PostgreSQL solo desde el EC2. Sin ingreso público.
resource "aws_security_group" "rds" {
  name        = "keibeauty-rds-sg"
  description = "PostgreSQL interno de KeiBeauty (solo EC2)"
  vpc_id      = data.aws_vpc.principal.id

  ingress {
    description     = "PostgreSQL desde el backend"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "keibeauty-rds-sg" }
}
