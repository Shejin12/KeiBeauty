# Cómputo (EC2) y base de datos (RDS). Réplica de:
# - Instancia i-0b0fc875e2a46f7caa, t3.micro, us-east-1c, key keibeauty-key
# - RDS keibeauty-db, PostgreSQL, db.t3.micro, us-east-1f, Multi-AZ No

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_instance" "backend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  availability_zone      = var.az_ec2
  subnet_id              = aws_subnet.publica.id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  key_name               = var.key_name

  tags = { Name = "keibeauty-backend" }
}

resource "aws_eip" "backend" {
  domain   = "vpc"
  instance = aws_instance.backend.id

  tags = { Name = "keibeauty-backend" }
}

resource "aws_db_subnet_group" "privado" {
  name       = "${var.proyecto}-privado"
  subnet_ids = [aws_subnet.privada_a.id, aws_subnet.privada_b.id]

  tags = { Name = "${var.proyecto}-privado" }
}

resource "aws_db_instance" "principal" {
  identifier             = var.db_identifier
  engine                 = "postgres"
  engine_version         = var.db_engine_version
  instance_class         = var.db_instance_class
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  allocated_storage      = 20
  storage_encrypted      = true
  multi_az               = false
  publicly_accessible    = false
  db_subnet_group_name   = aws_db_subnet_group.privado.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  backup_retention_period = 7
  deletion_protection    = true
  skip_final_snapshot    = false

  tags = { Name = var.db_identifier }
}
