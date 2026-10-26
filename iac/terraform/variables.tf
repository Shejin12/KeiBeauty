# Variables del stack KeiBeauty. Los valores por defecto reflejan la
# infraestructura real observada en la consola AWS (2026-10-26).
# Las credenciales (db_password, llaves) NUNCA van aquí: se pasan con
# -var, .tfvars ignorado o variables de entorno.

variable "region" {
  description = "Región AWS del despliegue"
  type        = string
  default     = "us-east-1"
}

variable "proyecto" {
  description = "Prefijo de nombres y etiquetas"
  type        = string
  default     = "keibeauty"
}

variable "vpc_id" {
  description = "VPC existente donde vive todo el stack"
  type        = string
  default     = "vpc-095111e509d685422"
}

variable "az_ec2" {
  description = "Zona de disponibilidad de la instancia EC2"
  type        = string
  default     = "us-east-1c"
}

variable "az_rds" {
  description = "Zona de disponibilidad de la instancia RDS"
  type        = string
  default     = "us-east-1f"
}

variable "key_name" {
  description = "Par de llaves SSH de la instancia EC2"
  type        = string
  default     = "keibeauty-key"
}

variable "db_identifier" {
  description = "Identificador de la instancia RDS"
  type        = string
  default     = "keibeauty-db"
}

variable "db_engine_version" {
  description = "Versión del motor PostgreSQL"
  type        = string
  default     = "16"
}

variable "db_instance_class" {
  description = "Clase de instancia RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Nombre de la base de datos inicial"
  type        = string
  default     = "keibeauty_db"
}

variable "db_username" {
  description = "Usuario maestro de RDS (el password va por variable sensible)"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Password maestro de RDS. Sin valor por defecto a propósito."
  type        = string
  sensitive   = true
}

variable "bucket_frontend" {
  description = "Bucket S3 del build del frontend"
  type        = string
  default     = "keibeauty-frontend"
}

variable "cloudfront_comment" {
  description = "Comentario de la distribución CloudFront"
  type        = string
  default     = "keibeauty-frontend"
}
