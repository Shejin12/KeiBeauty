import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailService:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.zoho.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_user)
        self.from_name = os.environ.get('FROM_NAME', 'KeiBeauty')

    def _send(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Envía un email usando SMTP"""
        if not self.smtp_user or not self.smtp_password:
            print('WARNING: SMTP credentials not configured, email not sent')
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email

            if text_body:
                msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f'Error sending email: {e}')
            return False

    def enviar_recuperacion_contrasena(self, to_email: str, nombre: str, token: str, frontend_url: str) -> bool:
        """Envía email con token de recuperación de contraseña"""
        reset_url = f'{frontend_url}/reestablecer-contrasena?token={token}'
        
        subject = 'Recuperación de contraseña - KeiBeauty'
        
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #eee; border-top: none; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #e91e63; color: white; padding: 14px 28px; text-decoration: none; border-radius: 50px; font-weight: 600; margin: 20px 0; }}
                .button:hover {{ background: #c2185b; }}
                .token {{ background: #f5f5f5; padding: 15px; border-radius: 8px; font-family: monospace; word-break: break-all; margin: 20px 0; }}
                .footer {{ text-align: center; color: #999; font-size: 0.85rem; margin-top: 30px; }}
                .warning {{ color: #c62828; font-size: 0.9rem; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>KeiBeauty</h1>
                    <p>Recuperación de contraseña</p>
                </div>
                <div class="content">
                    <h2>Hola {nombre},</h2>
                    <p>Recibimos una solicitud para restablecer tu contraseña. Si fuiste tú, haz clic en el botón de abajo:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Restablecer contraseña</a>
                    </p>
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <div class="token">{reset_url}</div>
                    <p class="warning"><strong>Importante:</strong> Este enlace expira en 24 horas y solo puede usarse una vez.</p>
                    <p>Si no solicitaste esto, ignora este email. Tu contraseña no cambiará.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 KeiBeauty. Cuidado de la piel coreano.</p>
                    <p>Si tienes problemas, contáctanos en soporte@keibeauty.com</p>
                </div>
            </div>
        </body>
        </html>
        '''

        text_body = f'''
        Hola {nombre},

        Recibimos una solicitud para restablecer tu contraseña en KeiBeauty.

        Para restablecer tu contraseña, visita:
        {reset_url}

        Este enlace expira en 24 horas y solo puede usarse una vez.

        Si no solicitaste esto, ignora este email.

        ---
        KeiBeauty - Cuidado de la piel coreano
        '''

        return self._send(to_email, subject, html_body, text_body)


# Instancia global
email_service = EmailService()