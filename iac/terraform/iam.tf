# Identidades CI por repo (B4). Mínimo privilegio: el usuario del frontend
# solo puede tocar SU bucket y SU distribución; el del backend no necesita
# permisos AWS porque el deploy entra por SSH (EC2_HOST/EC2_USERNAME/EC2_SSH_KEY).
#
# Estado real (2026-10-26): existe un solo usuario `github-actions-frontend`
# con AmazonS3FullAccess + CloudFrontFullAccess (demasiado amplio) y no existe
# usuario dedicado al backend. Estos recursos los reemplazan con alcance mínimo.
# El usuario humano `shjn` NO se gestiona aquí (ver runbook: acceso sin verificar).

resource "aws_iam_user" "github_actions_frontend" {
  name = "github-actions-frontend"
}

resource "aws_iam_policy" "frontend_deploy" {
  name        = "keibeauty-frontend-deploy"
  description = "Deploy del frontend: solo su bucket y su distribución"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "S3BucketPropio"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.frontend.arn]
      },
      {
        Sid      = "S3ObjetosPropios"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = ["${aws_s3_bucket.frontend.arn}/*"]
      },
      {
        Sid      = "CloudFrontPropia"
        Effect   = "Allow"
        Action   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
        Resource = [aws_cloudfront_distribution.frontend.arn]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "frontend_deploy" {
  user       = aws_iam_user.github_actions_frontend.name
  policy_arn = aws_iam_policy.frontend_deploy.arn
}

# Backend: sin políticas AWS. El deploy usa SSH al EC2, no la API de AWS.
resource "aws_iam_user" "github_actions_backend" {
  name = "github-actions-backend"
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend.id
}

output "frontend_distribution_domain" {
  value = aws_cloudfront_distribution.frontend.domain_name
}

output "backend_public_ip" {
  value = aws_eip.backend.public_ip
}

output "rds_endpoint" {
  value       = aws_db_instance.principal.endpoint
  description = "Endpoint interno (no público) de PostgreSQL"
}
