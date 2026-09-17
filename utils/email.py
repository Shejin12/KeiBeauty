import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailService:
    """Servicio de correo con paleta oficial KeiBeauty y estilos inline para clientes de correo."""

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
        """Envía email con token de recuperación de contraseña - paleta KeiBeauty"""
        reset_url = f'{frontend_url}/reestablecer-contrasena?token={token}'

        subject = 'Recuperación de contraseña - KeiBeauty'

        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0;padding:0;background-color:#F2F2F2;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height:1.6;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F2F2F2;padding:20px;">
                <tr><td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #D9D9D7;">
                        <tr>
                            <td style="background-color:#4D4D59;padding:32px;text-align:center;">
                                <h1 style="margin:0;color:#ffffff;font-size:24px;letter-spacing:1px;">KeiBeauty</h1>
                                <p style="margin:8px 0 0;color:#D9D9D7;font-size:14px;">Tu ritual esencial · Xela, Guatemala</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:32px 32px 8px;">
                                <h2 style="margin:0 0 12px;color:#3A3E40;font-size:20px;">Hola {nombre},</h2>
                                <p style="margin:0;color:#565659;font-size:15px;">Recibimos una solicitud para restablecer tu contraseña. Si fuiste tú, haz clic en el botón:</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:16px 32px;text-align:center;">
                                <a href="{reset_url}" style="display:inline-block;background-color:#4D4D59;color:#ffffff;padding:14px 36px;text-decoration:none;border-radius:50px;font-weight:600;font-size:15px;">Restablecer contraseña</a>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:8px 32px;">
                                <p style="margin:0 0 8px;color:#737166;font-size:13px;">O copia y pega este enlace en tu navegador:</p>
                                <div style="background:#F2F2F2;padding:12px 16px;border-radius:8px;font-family:monospace;font-size:12px;word-break:break-all;color:#3A3E40;border:1px solid #D9D9D7;">{reset_url}</div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:16px 32px;">
                                <p style="margin:0;padding:12px;background:#F2F2F2;border-left:4px solid #737166;border-radius:4px;color:#565659;font-size:13px;"><strong style="color:#3A3E40;">Importante:</strong> Este enlace expira en 24 horas y solo puede usarse una vez.</p>
                                <p style="margin:16px 0 0;color:#8C8A80;font-size:13px;">Si no solicitaste esto, ignora este email. Tu contraseña no cambiará.</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background:#3A3E40;padding:20px;text-align:center;">
                                <p style="margin:0;color:#D9D9D7;font-size:12px;">&copy; 2026 KeiBeauty. Cuidado de la piel coreano.</p>
                                <p style="margin:4px 0 0;color:#A6A498;font-size:11px;">Si tienes problemas, contáctanos en soporte@keibeauty.com</p>
                            </td>
                        </tr>
                    </table>
                </td></tr>
            </table>
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
        """Envía email de confirmación de pedido - paleta KeiBeauty"""
        subject = f'Confirmación de pedido #{pedido["id"]} - KeiBeauty'

        items_html = ''
        for detalle in pedido.get('detalles', []):
            producto = detalle.get('producto', {})
            items_html += f'''
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #D9D9D7; color:#3A3E40;">{producto.get('nombre', '')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #D9D9D7; text-align: center; color:#565659;">{detalle.get('cantidad', 0)}</td>
                <td style="padding: 12px; border-bottom: 1px solid #D9D9D7; text-align: right; color:#565659;">{self._format_price(detalle.get('precio_unitario', 0))}</td>
                <td style="padding: 12px; border-bottom: 1px solid #D9D9D7; text-align: right; color:#3A3E40; font-weight:600;">{self._format_price(detalle.get('subtotal', 0))}</td>
            </tr>
            '''

        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0;padding:0;background-color:#F2F2F2;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height:1.6;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F2F2F2;padding:20px;">
                <tr><td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #D9D9D7;">
                        <tr>
                            <td style="background-color:#4D4D59;padding:32px;text-align:center;">
                                <h1 style="margin:0;color:#ffffff;font-size:24px;">KeiBeauty</h1>
                                <p style="margin:8px 0 0;color:#D9D9D7;font-size:14px;">Gracias por tu pedido</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:32px;">
                                <h2 style="margin:0 0 8px;color:#3A3E40;font-size:20px;">Hola {nombre},</h2>
                                <p style="margin:0;color:#565659;">Tu pedido <strong style="color:#3A3E40;">#{pedido['id']}</strong> ha sido recibido y está siendo procesado.</p>
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;background:#F2F2F2;border-radius:8px;padding:16px;border:1px solid #D9D9D7;">
                                    <tr>
                                        <td style="padding:8px;color:#737166;font-size:13px;">Número de pedido:</td>
                                        <td style="padding:8px;text-align:right;color:#3A3E40;font-weight:600;">#{pedido['id']}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px;color:#737166;font-size:13px;">Fecha:</td>
                                        <td style="padding:8px;text-align:right;color:#3A3E40;">{pedido.get('fecha_pedido', '')[:10]}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px;color:#737166;font-size:13px;">Estado:</td>
                                        <td style="padding:8px;text-align:right;"><span style="background:#4D4D59;color:#fff;padding:4px 12px;border-radius:50px;font-size:12px;">{pedido.get('estado', 'pendiente').capitalize()}</span></td>
                                    </tr>
                                </table>
                                <h3 style="margin:0 0 12px;color:#3A3E40;font-size:16px;border-bottom:2px solid #A6A498;padding-bottom:8px;">Detalle del pedido</h3>
                                <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                                    <thead>
                                        <tr>
                                            <th style="background:#F2F2F2;padding:12px;text-align:left;color:#3A3E40;font-size:13px;border-bottom:2px solid #8C8A80;">Producto</th>
                                            <th style="background:#F2F2F2;padding:12px;text-align:center;color:#3A3E40;font-size:13px;border-bottom:2px solid #8C8A80;">Cant.</th>
                                            <th style="background:#F2F2F2;padding:12px;text-align:right;color:#3A3E40;font-size:13px;border-bottom:2px solid #8C8A80;">Precio</th>
                                            <th style="background:#F2F2F2;padding:12px;text-align:right;color:#3A3E40;font-size:13px;border-bottom:2px solid #8C8A80;">Subtotal</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items_html}
                                    </tbody>
                                </table>
                                <div style="text-align:right;margin-top:16px;padding-top:16px;border-top:1px solid #D9D9D7;">
                                    <span style="color:#737166;">Total: </span>
                                    <span style="color:#3A3E40;font-weight:700;font-size:18px;">{self._format_price(pedido.get('monto_total', 0))}</span>
                                </div>
                                <div style="background:#F2F2F2;padding:16px;border-radius:8px;margin:20px 0;border:1px solid #D9D9D7;">
                                    <strong style="color:#3A3E40;font-size:13px;">Dirección de envío:</strong><br>
                                    <span style="color:#565659;font-size:14px;">{pedido.get('direccion_envio', '')}</span>
                                </div>
                                <p style="margin:0;color:#565659;font-size:14px;">Te notificaremos cuando tu pedido sea enviado.</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background:#3A3E40;padding:20px;text-align:center;">
                                <p style="margin:0;color:#D9D9D7;font-size:12px;">&copy; 2026 KeiBeauty. Cuidado de la piel coreano.</p>
                                <p style="margin:4px 0 0;color:#A6A498;font-size:11px;">Preguntas? soporte@keibeauty.com · WhatsApp 3971 8418</p>
                            </td>
                        </tr>
                    </table>
                </td></tr>
            </table>
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
        """Envía email con código 2FA de 6 dígitos - paleta KeiBeauty"""
        subject = f'Tu código de acceso KeiBeauty: {codigo}'

        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0;padding:0;background-color:#F2F2F2;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height:1.6;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F2F2F2;padding:20px;">
                <tr><td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #D9D9D7;">
                        <tr>
                            <td style="background-color:#4D4D59;padding:32px;text-align:center;">
                                <h1 style="margin:0;color:#ffffff;font-size:24px;">KeiBeauty</h1>
                                <p style="margin:8px 0 0;color:#D9D9D7;font-size:14px;">Código de verificación</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:32px;text-align:center;">
                                <h2 style="margin:0 0 8px;color:#3A3E40;font-size:18px;">Tu código de acceso</h2>
                                <p style="margin:0;color:#565659;font-size:14px;">Usa el siguiente código para iniciar sesión:</p>
                                <div style="background:#F2F2F2;padding:20px;border-radius:12px;text-align:center;margin:20px 0;border:1px solid #D9D9D7;">
                                    <span style="font-size:36px;font-weight:700;letter-spacing:0.5rem;color:#4D4D59;font-family:monospace;">{codigo}</span>
                                </div>
                                <p style="margin:0;padding:12px;background:#F2F2F2;border-left:4px solid #737166;border-radius:4px;color:#565659;font-size:13px;text-align:left;"><strong style="color:#3A3E40;">Importante:</strong> Este código expira en {minutos_validez} minutos y solo puede usarse una vez.</p>
                                <p style="margin:16px 0 0;color:#8C8A80;font-size:13px;">Si no solicitaste esto, ignora este email. Tu cuenta está segura.</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="background:#3A3E40;padding:20px;text-align:center;">
                                <p style="margin:0;color:#D9D9D7;font-size:12px;">&copy; 2026 KeiBeauty. Cuidado de la piel coreano.</p>
                                <p style="margin:4px 0 0;color:#A6A498;font-size:11px;">soporte@keibeauty.com</p>
                            </td>
                        </tr>
                    </table>
                </td></tr>
            </table>
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

    def enviar_cambio_estado_pedido(self, to_email: str, nombre: str, pedido: dict, estado_anterior: str = None) -> bool:
        """Envía email cuando cambia el estado del pedido - paleta KeiBeauty"""
        subject = f'Actualización de tu pedido #{pedido["id"]} - KeiBeauty'
        estado = pedido.get('estado', 'pendiente').capitalize()
        html_body = f'''
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="margin:0;padding:0;background:#F2F2F2;font-family:sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#F2F2F2;padding:20px;"><tr><td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #D9D9D7;">
                    <tr><td style="background:#4D4D59;padding:24px;text-align:center;"><h1 style="margin:0;color:#fff;font-size:22px;">KeiBeauty</h1><p style="margin:4px 0 0;color:#D9D9D7;font-size:13px;">Actualización de pedido</p></td></tr>
                    <tr><td style="padding:32px;">
                        <h2 style="margin:0 0 8px;color:#3A3E40;">Hola {nombre},</h2>
                        <p style="color:#565659;">Tu pedido <strong>#{pedido["id"]}</strong> ha cambiado de estado.</p>
                        <div style="background:#F2F2F2;padding:16px;border-radius:8px;text-align:center;margin:16px 0;border:1px solid #D9D9D7;">
                            <span style="color:#737166;font-size:13px;">Nuevo estado:</span><br>
                            <span style="background:#4D4D59;color:#fff;padding:6px 16px;border-radius:50px;font-size:14px;font-weight:600;display:inline-block;margin-top:8px;">{estado}</span>
                        </div>
                        <p style="color:#565659;font-size:14px;">Dirección: {pedido.get('direccion_envio','')}</p>
                        <p style="color:#565659;font-size:14px;">Gracias por confiar en KeiBeauty.</p>
                    </td></tr>
                    <tr><td style="background:#3A3E40;padding:16px;text-align:center;"><p style="margin:0;color:#D9D9D7;font-size:12px;">&copy; 2026 KeiBeauty</p></td></tr>
                </table>
            </td></tr></table>
        </body></html>
        '''
        text_body = f'Hola {nombre}, tu pedido #{pedido["id"]} ahora está: {estado}'
        return self._send(to_email, subject, html_body, text_body)

    def enviar_bienvenida(self, to_email: str, nombre: str) -> bool:
        """Email de bienvenida - paleta KeiBeauty"""
        subject = 'Bienvenido a KeiBeauty - Tu ritual esencial'
        html_body = f'''
        <!DOCTYPE html>
        <html><head><meta charset="utf-8"></head>
        <body style="margin:0;padding:0;background:#F2F2F2;font-family:sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#F2F2F2;padding:20px;"><tr><td align="center">
                <table width="600" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #D9D9D7;">
                    <tr><td style="background:#4D4D59;padding:32px;text-align:center;"><h1 style="margin:0;color:#fff;">KeiBeauty</h1><p style="margin:8px 0 0;color:#D9D9D7;">Tu ritual esencial</p></td></tr>
                    <tr><td style="padding:32px;">
                        <h2 style="color:#3A3E40;">Bienvenido, {nombre}</h2>
                        <p style="color:#565659;">Gracias por unirte a KeiBeauty. Descubre lo mejor del K-Beauty auténtico.</p>
                        <p style="text-align:center;margin:24px 0;"><a href="#" style="display:inline-block;background:#4D4D59;color:#fff;padding:12px 28px;text-decoration:none;border-radius:50px;font-weight:600;">Explorar catálogo</a></p>
                    </td></tr>
                    <tr><td style="background:#3A3E40;padding:16px;text-align:center;color:#D9D9D7;font-size:12px;">&copy; 2026 KeiBeauty</td></tr>
                </table>
            </td></tr></table>
        </body></html>
        '''
        return self._send(to_email, subject, html_body, f'Bienvenido {nombre} a KeiBeauty')


# Instancia global
email_service = EmailService()
