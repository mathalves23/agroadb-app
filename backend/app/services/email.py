"""
Sistema de Notificações por Email
Envia notificações para usuários sobre eventos importantes
"""

import logging
import os
import smtplib
import ssl
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class EmailService:
    """
    Serviço de Envio de Emails

    Suporta templates HTML, anexos e notificações transacionais
    """

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = 587,
        smtp_user: str = None,
        smtp_password: str = None,
        from_email: str = None,
        from_name: str = "AgroADB",
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = from_name

        # Setup Jinja2 para templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        template_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Envia email

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML
            text_content: Conteúdo texto plano (fallback)
            attachments: Lista de anexos

        Returns:
            True se enviado com sucesso
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Adicionar conteúdo
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))

            msg.attach(MIMEText(html_content, "html"))

            # Adicionar anexos
            if attachments:
                for attachment in attachments:
                    # TODO: Implementar anexos
                    pass

            # Enviar
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✅ Email enviado para {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao enviar email para {to_email}: {e}")
            return False

    async def send_investigation_completed(
        self,
        to_email: str,
        user_name: str,
        investigation_id: str,
        investigation_name: str,
        total_results: int,
        completed_at: datetime,
        dashboard_url: str,
    ) -> bool:
        """
        Envia notificação de investigação concluída

        Args:
            to_email: Email do usuário
            user_name: Nome do usuário
            investigation_id: ID da investigação
            investigation_name: Nome da investigação
            total_results: Total de resultados encontrados
            completed_at: Data/hora de conclusão
            dashboard_url: URL para acessar resultados

        Returns:
            True se enviado com sucesso
        """
        subject = f"✅ Investigação Concluída: {investigation_name}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #16a34a; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background: #f9fafb; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #16a34a; 
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .stats {{ background: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Investigação Concluída!</h1>
        </div>
        
        <div class="content">
            <p>Olá, <strong>{user_name}</strong>!</p>
            
            <p>Sua investigação foi concluída com sucesso:</p>
            
            <div class="stats">
                <h3>📋 {investigation_name}</h3>
                <p><strong>ID:</strong> {investigation_id}</p>
                <p><strong>Resultados encontrados:</strong> {total_results}</p>
                <p><strong>Concluída em:</strong> {completed_at.strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
            
            <p>Acesse a plataforma para visualizar os resultados completos:</p>
            
            <a href="{dashboard_url}" class="button">Ver Resultados</a>
            
            <p>Os resultados incluem:</p>
            <ul>
                <li>✅ Dados cadastrais e documentos</li>
                <li>✅ Propriedades e imóveis rurais</li>
                <li>✅ Vínculos societários</li>
                <li>✅ Registros em diários oficiais</li>
                <li>✅ Análise geoespacial</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>AgroADB - Sistema de Inteligência Patrimonial</p>
            <p>Este é um email automático. Não responda.</p>
        </div>
    </div>
</body>
</html>
        """

        text_content = f"""
Olá, {user_name}!

Sua investigação foi concluída com sucesso:

📋 {investigation_name}
ID: {investigation_id}
Resultados encontrados: {total_results}
Concluída em: {completed_at.strftime('%d/%m/%Y às %H:%M')}

Acesse a plataforma para visualizar os resultados completos:
{dashboard_url}

---
AgroADB - Sistema de Inteligência Patrimonial
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_investigation_failed(
        self,
        to_email: str,
        user_name: str,
        investigation_id: str,
        investigation_name: str,
        error_message: str,
    ) -> bool:
        """Envia notificação de falha na investigação"""
        subject = f"❌ Erro na Investigação: {investigation_name}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background: #f9fafb; }}
        .error {{ background: #fee2e2; padding: 15px; border-left: 4px solid #dc2626; margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #dc2626; 
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Erro na Investigação</h1>
        </div>
        
        <div class="content">
            <p>Olá, <strong>{user_name}</strong>,</p>
            
            <p>Infelizmente ocorreu um erro ao processar sua investigação:</p>
            
            <div class="error">
                <h3>📋 {investigation_name}</h3>
                <p><strong>ID:</strong> {investigation_id}</p>
                <p><strong>Erro:</strong> {error_message}</p>
            </div>
            
            <p>Nossa equipe foi notificada e está trabalhando para resolver o problema.</p>
            
            <p>Você pode:</p>
            <ul>
                <li>Tentar novamente mais tarde</li>
                <li>Entrar em contato com o suporte</li>
            </ul>
            
            <a href="mailto:support@agroadb.com" class="button">Falar com Suporte</a>
        </div>
        
        <div class="footer">
            <p>AgroADB - Sistema de Inteligência Patrimonial</p>
            <p>Este é um email automático. Não responda.</p>
        </div>
    </div>
</body>
</html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_welcome_email(self, to_email: str, user_name: str, dashboard_url: str) -> bool:
        """Envia email de boas-vindas"""
        subject = "🎉 Bem-vindo ao AgroADB!"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #16a34a; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background: #f9fafb; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #16a34a; 
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 Bem-vindo ao AgroADB!</h1>
        </div>
        
        <div class="content">
            <p>Olá, <strong>{user_name}</strong>!</p>
            
            <p>Obrigado por se cadastrar no AgroADB, a plataforma de inteligência 
            patrimonial para o agronegócio brasileiro.</p>
            
            <p>Com nossa plataforma você pode:</p>
            <ul>
                <li>🔍 Investigar propriedades rurais</li>
                <li>📊 Analisar vínculos societários</li>
                <li>🗺️ Visualizar dados geoespaciais</li>
                <li>📋 Gerar relatórios profissionais</li>
            </ul>
            
            <a href="{dashboard_url}" class="button">Acessar Plataforma</a>
            
            <p>Precisa de ajuda? Entre em contato com nossa equipe:</p>
            <p>📧 support@agroadb.com</p>
        </div>
        
        <div class="footer">
            <p>AgroADB - Sistema de Inteligência Patrimonial</p>
        </div>
    </div>
</body>
</html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_2fa_enabled_notification(self, to_email: str, user_name: str) -> bool:
        """Notifica usuário que 2FA foi habilitado"""
        subject = "🔒 Autenticação de Dois Fatores Ativada"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #0ea5e9; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; background: #f9fafb; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 2FA Ativado</h1>
        </div>
        
        <div class="content">
            <p>Olá, <strong>{user_name}</strong>,</p>
            
            <p>A autenticação de dois fatores foi ativada na sua conta.</p>
            
            <p>A partir de agora, você precisará do código do seu app autenticador 
            para fazer login.</p>
            
            <p><strong>Importante:</strong> Guarde seus códigos de backup em local seguro!</p>
            
            <p>Se você não reconhece esta ação, entre em contato imediatamente:</p>
            <p>📧 security@agroadb.com</p>
        </div>
        
        <div class="footer">
            <p>AgroADB - Sistema de Inteligência Patrimonial</p>
        </div>
    </div>
</body>
</html>
        """

        return await self.send_email(to_email, subject, html_content)


# Instância global
email_service = EmailService()
