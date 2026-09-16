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

    def enviar_confirmacion_pedido(self, to_email: str, nombre: str, pedido: dict) -> bool:
        """Envía email de confirmación de pedido"""
        subject = f'Confirmación de pedido #{pedido["id"]} - KeiBeauty'
        
        items_html = ''
        for detalle in pedido.get('detalles', []):
            producto = detalle.get('producto', {})
            items_html += f'''
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{producto.get('nombre', '')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">{detalle.get('cantidad', 0)}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">{self._format_price(detalle.get('precio_unitario', 0))}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">{self._format_price(detalle.get('subtotal', 0))}</td>
            </tr>
            '''
        
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
                .order-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .order-info-row {{ display: flex; justify-content: space-between; margin: 8px 0; }}
                .order-info-label {{ color: #666; }}
                .order-info-value {{ font-weight: 600; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f5f5f5; padding: 12px; text-align: left; border-bottom: 2px solid #e91e63; }}
                td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                .total-row {{ font-weight: 700; font-size: 1.1rem; }}
                .footer {{ text-align: center; color: #999; font-size: 0.85rem; margin-top: 30px; }}
                .address-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>KeiBeauty</h1>
                    <p>¡Gracias por tu pedido!</p>
                </div>
                <div class="content">
                    <h2>Hola {nombre},</h2>
                    <p>Tu pedido <strong>#{pedido['id']}</strong> ha sido recibido y está siendo procesado.</p>
                    
                    <div class="order-info">
                        <div class="order-info-row">
                            <span class="order-info-label">Número de pedido:</span>
                            <span class="order-info-value">#{pedido['id']}</span>
                        </div>
                        <div class="order-info-row">
                            <span class="order-info-label">Fecha:</span>
                            <span class="order-info-value">{pedido.get('fecha_pedido', '')[:10]}</span>
                        </div>
                        <div class="order-info-row">
                            <span class="order-info-label">Estado:</span>
                            <span class="order-info-value">{pedido.get('estado', 'pendiente').capitalize()}</span>
                        </div>
                    </div>
                    
                    <h3>Detalle del pedido</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th style="text-align: center;">Cant.</th>
                                <th style="text-align: right;">Precio</th>
                                <th style="text-align: right;">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="order-info-row total-row" style="text-align: right; font-size: 1.2rem; margin-top: 15px;">
                        <span>Total: </span>
                        <span>{self._format_price(pedido.get('monto_total', 0))}</span>
                    </div>
                    
                    <div class="address-box">
                        <strong>Dirección de envío:</strong><br>
                        {pedido.get('direccion_envio', '')}
                    </div>
                    
                    <p>Te notificaremos cuando tu pedido sea enviado.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 KeiBeauty. Cuidado de la piel coreano.</p>
                    <p>Si tienes preguntas, contáctanos en soporte@keibeauty.com</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        text_body = f'''
        Hola {nombre},

        Tu pedido #{pedido['id']} ha sido recibido.
        Total: {self._format_price(pedido.get('monto_total', 0))}
        Dirección: {pedido.get('direccion_envio', '')}
        
        Gracias por tu compra.
        KeiBeauty
        '''

        return self._send(to_email, subject, html_body, text_body)
    
    def _format_price(self, price):
        """Formatea precio en GTQ"""
        return f'Q {float(price):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    def enviar_codigo_2fa(self, to_email: str, codigo: str, minutos_validez: int = 5) -> bool:
        """Envía email con código 2FA de 6 dígitos"""
        subject = f'Tu código de acceso KeiBeauty: {codigo}'
        
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
                .code-box {{ background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .code {{ font-size: 2.5rem; font-weight: 700; letter-spacing: 0.5rem; color: #e91e63; font-family: monospace; }}
                .footer {{ text-align: center; color: #999; font-size: 0.85rem; margin-top: 30px; }}
                .warning {{ color: #c62828; font-size: 0.9rem; }}
            </style>
        </head>
        <html>
        <body>
            <div class="container">
                <div class="header">
                    <h1>KeiBeauty</h1>
                    <p>Código de verificación</p>
                </div>
                <div class="content">
                    <h2>Tu código de acceso</h2>
                    <p>Usa el siguiente código para iniciar sesión en KeiBeauty:</p>
                    <div class="code-box">
                        <span class="code">{codigo}</span>
                    </div>
                    <p class="warning"><strong>Importante:</strong> Este código expira en {minutos_validez} minutos y solo puede usarse una vez.</p>
                    <p>Si no solicitaste esto, ignora este email. Tu cuenta está segura.</p>
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
        Tu código de acceso KeiBeauty es: {codigo}

        Este código expira en {minutos_validez} minutos y solo puede usarse una vez.

        Si no solicitaste esto, ignora este email.

        ---
        KeiBeauty - Cuidado de la piel coreano
        '''

        with open('/tmp/codigo_2fa.txt', 'w') as f:
            f.write(str(codigo))
        return self._send(to_email, subject, html_body, text_body)


# Instancia global
email_service = EmailService()