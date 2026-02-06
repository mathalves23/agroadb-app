"""
Email Service - Envio de emails com templates HTML
"""
from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from jinja2 import Template

from app.core.config import settings
from app.domain.notification import NotificationType
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Serviço para envio de emails"""
    
    @staticmethod
    def _get_smtp_connection():
        """Cria conexão SMTP"""
        try:
            smtp_host = settings.SMTP_HOST
            smtp_port = settings.SMTP_PORT
            smtp_user = settings.SMTP_USER
            smtp_password = settings.SMTP_PASSWORD
            
            if not smtp_user or not smtp_password:
                logger.warning("SMTP credentials not configured")
                return None
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            return server
        except Exception as e:
            logger.error(f"Erro ao conectar SMTP: {e}")
            return None
    
    @staticmethod
    def _load_template(template_name: str, context: Dict[str, Any]) -> str:
        """
        Carrega e renderiza template HTML
        
        Args:
            template_name: Nome do arquivo de template (ex: 'investigation_completed.html')
            context: Dicionário com variáveis para o template
            
        Returns:
            HTML renderizado
        """
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        template_path = template_dir / template_name
        
        # Se template não existe, usar fallback inline
        if not template_path.exists():
            logger.warning(f"Template {template_name} não encontrado, usando fallback")
            return EmailService._get_fallback_template(context)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Erro ao carregar template {template_name}: {e}")
            return EmailService._get_fallback_template(context)
    
    @staticmethod
    def _get_fallback_template(context: Dict[str, Any]) -> str:
        """Template HTML fallback caso o arquivo não exista"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 32px;">
                    <tr>
                        <td>
                            <h1 style="color: #10b981; margin: 0 0 24px;">AgroADB</h1>
                            <p>Olá, <strong>{context.get('user_name', 'Usuário')}</strong>!</p>
                            <div style="margin: 24px 0;">
                                {context.get('message', 'Você tem uma nova notificação.')}
                            </div>
                            <p style="color: #6b7280; font-size: 14px; margin-top: 32px;">
                                Equipe AgroADB
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
    
    @staticmethod
    async def send_notification_email(
        to_email: str,
        user_name: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        action_url: Optional[str] = None
    ):
        """Envia email de notificação com template HTML"""
        
        # Obter template HTML
        html_content = EmailService._get_notification_template(
            user_name=user_name,
            title=title,
            message=message,
            action_url=action_url,
            notification_type=notification_type
        )
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"AgroADB - {title}"
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        msg['To'] = to_email
        
        # Texto simples (fallback)
        text_part = MIMEText(f"{title}\n\n{message}", 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Enviar
        try:
            server = EmailService._get_smtp_connection()
            if server:
                server.send_message(msg)
                server.quit()
                logger.info(f"Email enviado para {to_email}")
                return True
            else:
                logger.warning(f"SMTP não configurado, email não enviado para {to_email}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    @staticmethod
    def _get_notification_template(
        user_name: str,
        title: str,
        message: str,
        action_url: Optional[str],
        notification_type: NotificationType
    ) -> str:
        """Gera template HTML para email de notificação"""
        
        # Cores por tipo
        colors = {
            NotificationType.INVESTIGATION_CREATED: "#3B82F6",  # blue
            NotificationType.INVESTIGATION_SHARED: "#8B5CF6",   # purple
            NotificationType.INVESTIGATION_COMMENT: "#10B981",  # green
            NotificationType.REPORT_READY: "#059669",           # emerald
            NotificationType.QUERY_COMPLETED: "#14B8A6",        # teal
            NotificationType.ALERT: "#EF4444"                   # red
        }
        color = colors.get(notification_type, "#6B7280")
        
        action_button = ""
        if action_url:
            base_url = settings.FRONTEND_URL
            full_url = f"{base_url}{action_url}"
            action_button = f'''
            <tr>
                <td style="padding: 20px 0;">
                    <a href="{full_url}" 
                       style="background-color: {color}; 
                              color: white; 
                              padding: 12px 24px; 
                              text-decoration: none; 
                              border-radius: 6px; 
                              display: inline-block;
                              font-weight: 600;">
                        Ver Detalhes
                    </a>
                </td>
            </tr>
            '''
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f3f4f6;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 32px 32px 24px; border-bottom: 1px solid #e5e7eb;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #111827;">
                                            AgroADB
                                        </h1>
                                        <p style="margin: 4px 0 0; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">
                                            Intelligence Platform
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 32px;">
                            <p style="margin: 0 0 16px; font-size: 16px; color: #374151;">
                                Olá, <strong>{user_name}</strong>
                            </p>
                            
                            <div style="background-color: {color}15; border-left: 4px solid {color}; padding: 16px; border-radius: 4px; margin: 24px 0;">
                                <h2 style="margin: 0 0 8px; font-size: 18px; font-weight: 600; color: #111827;">
                                    {title}
                                </h2>
                                <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.6;">
                                    {message}
                                </p>
                            </div>
                            
                            {action_button}
                            
                            <p style="margin: 24px 0 0; font-size: 14px; color: #6b7280; line-height: 1.6;">
                                Esta é uma notificação automática do sistema AgroADB. 
                                Para gerenciar suas preferências de notificação, acesse as 
                                <a href="{settings.FRONTEND_URL}/profile" 
                                   style="color: {color}; text-decoration: none;">
                                    configurações do seu perfil
                                </a>.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 32px; border-top: 1px solid #e5e7eb; background-color: #f9fafb;">
                            <p style="margin: 0; font-size: 12px; color: #9ca3af; text-align: center;">
                                © {datetime.now().year} AgroADB. Todos os direitos reservados.<br>
                                Sistema de Inteligência para Due Diligence Rural
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        '''
    
    @staticmethod
    async def send_welcome_email(to_email: str, user_name: str, username: str):
        """Envia email de boas-vindas"""
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 40px 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 32px;">
        <h1 style="color: #10b981; margin: 0 0 24px;">Bem-vindo ao AgroADB! 🎉</h1>
        
        <p>Olá, <strong>{user_name}</strong>!</p>
        
        <p>Sua conta foi criada com sucesso. Você já pode começar a usar a plataforma.</p>
        
        <p><strong>Seus dados de acesso:</strong></p>
        <ul>
            <li>Usuário: <code>{username}</code></li>
            <li>Email: <code>{to_email}</code></li>
        </ul>
        
        <a href="{settings.FRONTEND_URL}/login" 
           style="display: inline-block; background-color: #10b981; color: white; padding: 12px 24px; 
                  text-decoration: none; border-radius: 6px; margin: 20px 0;">
            Acessar Plataforma
        </a>
        
        <p style="color: #6b7280; font-size: 14px; margin-top: 32px;">
            Equipe AgroADB
        </p>
    </div>
</body>
</html>
        '''
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Bem-vindo ao AgroADB!"
        msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
        msg['To'] = to_email
        
        msg.attach(MIMEText(html_content, 'html'))
        
        try:
            server = EmailService._get_smtp_connection()
            if server:
                server.send_message(msg)
                server.quit()
                return True
        except Exception as e:
            logger.error(f"Erro ao enviar email de boas-vindas: {e}")
        
        return False
    
    @staticmethod
    async def send_investigation_completed(
        user_email: str,
        user_name: str,
        investigation: Dict[str, Any]
    ) -> bool:
        """
        Envia email quando investigação é concluída
        
        Args:
            user_email: Email do usuário
            user_name: Nome do usuário
            investigation: Dados da investigação (dict com id, target_name, properties_found, etc)
            
        Returns:
            True se enviado com sucesso
        """
        try:
            context = {
                'user_name': user_name,
                'investigation_id': investigation.get('id'),
                'target_name': investigation.get('target_name'),
                'properties_found': investigation.get('properties_found', 0),
                'companies_found': investigation.get('companies_found', 0),
                'lease_contracts_found': investigation.get('lease_contracts_found', 0),
                'frontend_url': settings.FRONTEND_URL,
                'year': datetime.now().year
            }
            
            html_content = EmailService._load_template('investigation_completed.html', context)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AgroADB - Investigação Concluída: {context['target_name']}"
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
            msg['To'] = user_email
            
            # Fallback texto simples
            text_content = f"""
Olá, {user_name}!

Sua investigação sobre {context['target_name']} foi concluída com sucesso.

Resultados encontrados:
- Propriedades: {context['properties_found']}
- Empresas: {context['companies_found']}
- Contratos: {context['lease_contracts_found']}

Acesse a plataforma para ver os detalhes completos:
{context['frontend_url']}/investigations/{context['investigation_id']}

Equipe AgroADB
            """
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            server = EmailService._get_smtp_connection()
            if server:
                server.send_message(msg)
                server.quit()
                logger.info(f"✅ Email de investigação concluída enviado para {user_email}")
                return True
            else:
                logger.warning(f"SMTP não configurado, email não enviado para {user_email}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar email de investigação concluída: {e}")
            return False
    
    @staticmethod
    async def send_investigation_shared(
        user_email: str,
        user_name: str,
        investigation: Dict[str, Any],
        shared_by_name: str,
        permission_level: str
    ) -> bool:
        """
        Envia email quando investigação é compartilhada
        
        Args:
            user_email: Email do usuário que receberá o compartilhamento
            user_name: Nome do usuário
            investigation: Dados da investigação
            shared_by_name: Nome de quem compartilhou
            permission_level: Nível de permissão (view, comment, edit, admin)
            
        Returns:
            True se enviado com sucesso
        """
        try:
            permission_labels = {
                'view': 'Visualização',
                'comment': 'Visualização e Comentários',
                'edit': 'Edição',
                'admin': 'Administração completa'
            }
            
            context = {
                'user_name': user_name,
                'shared_by_name': shared_by_name,
                'investigation_id': investigation.get('id'),
                'target_name': investigation.get('target_name'),
                'permission_level': permission_level,
                'permission_label': permission_labels.get(permission_level, permission_level),
                'frontend_url': settings.FRONTEND_URL,
                'year': datetime.now().year
            }
            
            html_content = EmailService._load_template('investigation_shared.html', context)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AgroADB - Investigação Compartilhada: {context['target_name']}"
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM}>"
            msg['To'] = user_email
            
            # Fallback texto simples
            text_content = f"""
Olá, {user_name}!

{shared_by_name} compartilhou uma investigação com você.

Investigação: {context['target_name']}
Permissão: {context['permission_label']}

Acesse a plataforma para visualizar:
{context['frontend_url']}/investigations/{context['investigation_id']}

Equipe AgroADB
            """
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            server = EmailService._get_smtp_connection()
            if server:
                server.send_message(msg)
                server.quit()
                logger.info(f"✅ Email de compartilhamento enviado para {user_email}")
                return True
            else:
                logger.warning(f"SMTP não configurado, email não enviado para {user_email}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar email de compartilhamento: {e}")
            return False
