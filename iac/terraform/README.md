# IaC KeiBeauty (Fase 3)

Réplica declarativa de la infraestructura AWS real (cuenta 887762371814,
región `us-east-1`, observada el 2026-10-26). **No aplicar sin revisión**:
los recursos ya existen.

## Arquitectura

```text
Usuarios ──HTTPS──▶ CloudFront (keibeauty-frontend)
                        │  OAC (solo CloudFront lee el bucket)
                        ▼
                   S3 keibeauty-frontend (privado: assets/, index.html)

GitHub Actions ──SSH──▶ EC2 keibeauty-backend (t3.micro, nginx + gunicorn)
                            │  SG: 5432 solo desde EC2
                            ▼
                    RDS keibeauty-db (PostgreSQL, db.t3.micro,
                    subredes privadas, sin acceso público)
```

## Uso

```bash
cd iac/terraform
terraform init
terraform validate
terraform plan -var="db_password=..."   # solo lectura del plan
```

`db_password` no tiene valor por defecto a propósito: se pasa con `-var`
o `TF_VAR_db_password`.

## B4 — roles IAM por repo

- `github-actions-frontend`: solo su bucket y su distribución (reemplaza el
  `AmazonS3FullAccess` + `CloudFrontFullAccess` actuales, demasiado amplios).
- `github-actions-backend`: sin políticas AWS (el deploy entra por SSH con
  los secretos `EC2_HOST`/`EC2_USERNAME`/`EC2_SSH_KEY`).
- El usuario humano `shjn` no se gestiona aquí (acceso sin verificar; ver
  runbook antes de tocarlo).
