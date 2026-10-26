# Réplica declarativa de la infraestructura AWS real de KeiBeauty (Fase 3).
#
# Origen: capturas de la consola AWS del 2026-10-26 (cuenta 887762371814,
# región us-east-1). La base de datos vive en la red interna (RDS privado,
# sin acceso público) y solo el EC2 la alcanza por el SG.
#
# NO aplicar sin revisión: los recursos ya existen y un `terraform apply`
# podría recrearlos. Sirve como documentación versionada y como base para
# recrear el entorno.

terraform {
  required_version = ">= 1.6.0"

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
