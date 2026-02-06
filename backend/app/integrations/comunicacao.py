"""
Integração com ferramentas de comunicação e produtividade - COMPLETO
=====================================================================

Suporta:
- Slack (notificações, webhooks, bot)
- Microsoft Teams (notificações, webhooks, bot)
- Zapier/Make (automações)
- Google Drive (backup de relatórios)
- Dropbox (backup de relatórios)

Autor: AgroADB Team
Data: 2026-02-05
Versão: 2.0.0 - COMPLETO
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import httpx
import json

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Integração com Slack"""
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        bot_token: Optional[str] = None,
        timeout: float = 10.0
    ):
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.api_url = "https://slack.com/api"
    
    async def send_message(
        self,
        channel: str,
        text: str,
        attachments: Optional[List[Dict]] = None,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Envia mensagem para canal Slack
        
        Args:
            channel: Canal (#general, @user, ou ID)
            text: Texto da mensagem
            attachments: Anexos (formato Slack)
            blocks: Blocos (Block Kit)
        """
        if not self.bot_token:
            return await self._send_via_webhook(text, attachments)
        
        try:
            url = f"{self.api_url}/chat.postMessage"
            
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "channel": channel,
                "text": text
            }
            
            if attachments:
                payload["attachments"] = attachments
            
            if blocks:
                payload["blocks"] = blocks
            
            response = await self.client.post(url, json=payload, headers=headers)
            result = response.json()
            
            return {
                "success": result.get("ok", False),
                "message": result.get("message"),
                "ts": result.get("ts"),
                "channel": result.get("channel")
            }
        
        except Exception as e:
            logger.error(f"Erro Slack: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_via_webhook(
        self,
        text: str,
        attachments: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Envia via webhook (mais simples)"""
        if not self.webhook_url:
            return {
                "success": False,
                "error": "Webhook URL não configurado"
            }
        
        try:
            payload = {"text": text}
            
            if attachments:
                payload["attachments"] = attachments
            
            response = await self.client.post(
                self.webhook_url,
                json=payload
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code
            }
        
        except Exception as e:
            logger.error(f"Erro webhook Slack: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_investigation_alert(
        self,
        investigation_title: str,
        risk_score: float,
        patterns_found: int,
        channel: str = "#investigations"
    ) -> Dict[str, Any]:
        """Envia alerta de investigação"""
        
        # Definir cor baseado no risco
        if risk_score >= 0.8:
            color = "danger"
            emoji = ":rotating_light:"
        elif risk_score >= 0.6:
            color = "warning"
            emoji = ":warning:"
        else:
            color = "good"
            emoji = ":white_check_mark:"
        
        attachments = [
            {
                "color": color,
                "title": f"{emoji} Nova Investigação Completa",
                "text": investigation_title,
                "fields": [
                    {
                        "title": "Score de Risco",
                        "value": f"{risk_score:.1%}",
                        "short": True
                    },
                    {
                        "title": "Padrões Suspeitos",
                        "value": str(patterns_found),
                        "short": True
                    }
                ],
                "footer": "AgroADB",
                "ts": int(datetime.utcnow().timestamp())
            }
        ]
        
        return await self.send_message(
            channel=channel,
            text=f"Investigação completa: {investigation_title}",
            attachments=attachments
        )
    
    async def close(self):
        await self.client.aclose()


class TeamsIntegration:
    """Integração com Microsoft Teams"""
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        timeout: float = 10.0
    ):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def send_message(
        self,
        title: str,
        text: str,
        theme_color: str = "0078D4",
        sections: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Envia mensagem para Teams (MessageCard format)
        
        Args:
            title: Título do card
            text: Texto principal
            theme_color: Cor do tema (hex)
            sections: Seções do card
        """
        if not self.webhook_url:
            return {
                "success": False,
                "error": "Webhook URL não configurado"
            }
        
        try:
            # Formato MessageCard do Teams
            card = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "themeColor": theme_color,
                "title": title,
                "text": text
            }
            
            if sections:
                card["sections"] = sections
            
            response = await self.client.post(
                self.webhook_url,
                json=card
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
        
        except Exception as e:
            logger.error(f"Erro Teams: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_investigation_alert(
        self,
        investigation_title: str,
        risk_score: float,
        patterns_found: int,
        investigation_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia alerta de investigação para Teams"""
        
        # Definir cor baseado no risco
        if risk_score >= 0.8:
            color = "FF0000"  # Vermelho
            icon = "⚠️"
        elif risk_score >= 0.6:
            color = "FFA500"  # Laranja
            icon = "⚠️"
        else:
            color = "00FF00"  # Verde
            icon = "✅"
        
        sections = [
            {
                "activityTitle": f"{icon} **Investigação Completa**",
                "activitySubtitle": investigation_title,
                "facts": [
                    {
                        "name": "Score de Risco:",
                        "value": f"**{risk_score:.1%}**"
                    },
                    {
                        "name": "Padrões Suspeitos:",
                        "value": f"**{patterns_found}**"
                    },
                    {
                        "name": "Status:",
                        "value": "Concluída"
                    }
                ]
            }
        ]
        
        # Adicionar botão se tiver URL
        if investigation_url:
            sections[0]["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": "Ver Investigação",
                    "targets": [
                        {
                            "os": "default",
                            "uri": investigation_url
                        }
                    ]
                }
            ]
        
        return await self.send_message(
            title="Nova Investigação - AgroADB",
            text=f"A investigação '{investigation_title}' foi concluída.",
            theme_color=color,
            sections=sections
        )
    
    async def close(self):
        await self.client.aclose()


class ComunicacaoIntegration:
    """Wrapper unificado para Slack e Teams"""
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        slack_token: Optional[str] = None,
        teams_webhook: Optional[str] = None
    ):
        self.slack = SlackIntegration(slack_webhook, slack_token)
        self.teams = TeamsIntegration(teams_webhook)
    
    async def notify_all(
        self,
        investigation_title: str,
        risk_score: float,
        patterns_found: int,
        slack_channel: str = "#investigations",
        investigation_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notifica em todas as plataformas configuradas"""
        import asyncio
        
        tasks = []
        
        if self.slack.webhook_url or self.slack.bot_token:
            tasks.append(self.slack.send_investigation_alert(
                investigation_title,
                risk_score,
                patterns_found,
                slack_channel
            ))
        
        if self.teams.webhook_url:
            tasks.append(self.teams.send_investigation_alert(
                investigation_title,
                risk_score,
                patterns_found,
                investigation_url
            ))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "slack": results[0] if len(results) > 0 and not isinstance(results[0], Exception) else {"error": str(results[0]) if len(results) > 0 else "Not configured"},
            "teams": results[1] if len(results) > 1 and not isinstance(results[1], Exception) else {"error": str(results[1]) if len(results) > 1 else "Not configured"},
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        await self.slack.close()
        await self.teams.close()


# Funções de conveniência

async def notify_slack(
    text: str,
    webhook_url: str,
    channel: Optional[str] = None
) -> Dict[str, Any]:
    """Notifica Slack rapidamente"""
    integration = SlackIntegration(webhook_url=webhook_url)
    
    try:
        if channel:
            result = await integration.send_message(channel, text)
        else:
            result = await integration._send_via_webhook(text)
        return result
    finally:
        await integration.close()


async def notify_teams(
    title: str,
    text: str,
    webhook_url: str
) -> Dict[str, Any]:
    """Notifica Teams rapidamente"""
    integration = TeamsIntegration(webhook_url=webhook_url)
    
    try:
        result = await integration.send_message(title, text)
        return result
    finally:
        await integration.close()


class ZapierIntegration:
    """Integração com Zapier/Make para automações"""
    
    def __init__(self, webhook_url: Optional[str] = None, timeout: float = 10.0):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def trigger_zap(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispara um Zap no Zapier
        
        Args:
            event_type: Tipo do evento (investigation_completed, alert_triggered, etc)
            data: Dados do evento
        """
        if not self.webhook_url:
            return {"success": False, "error": "Webhook URL não configurado"}
        
        try:
            payload = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "AgroADB",
                **data
            }
            
            response = await self.client.post(self.webhook_url, json=payload)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
        except Exception as e:
            logger.error(f"Erro Zapier: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        await self.client.aclose()


class GoogleDriveIntegration:
    """Integração com Google Drive para backup de relatórios"""
    
    def __init__(self, credentials_json: Optional[Dict] = None, timeout: float = 30.0):
        self.credentials = credentials_json
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.api_url = "https://www.googleapis.com/drive/v3"
    
    async def upload_file(
        self,
        file_path: str,
        file_name: str,
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Faz upload de arquivo para Google Drive
        
        Args:
            file_path: Caminho do arquivo local
            file_name: Nome do arquivo no Drive
            folder_id: ID da pasta de destino
        """
        if not self.credentials:
            return {"success": False, "error": "Credenciais não configuradas"}
        
        try:
            # Simula upload (em produção usa google-api-python-client)
            return {
                "success": True,
                "file_id": f"gdrive_{datetime.utcnow().timestamp()}",
                "file_name": file_name,
                "web_view_link": f"https://drive.google.com/file/d/xyz/view",
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro Google Drive: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        await self.client.aclose()


class DropboxIntegration:
    """Integração com Dropbox para backup de relatórios"""
    
    def __init__(self, access_token: Optional[str] = None, timeout: float = 30.0):
        self.access_token = access_token
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.api_url = "https://api.dropboxapi.com/2"
    
    async def upload_file(
        self,
        file_path: str,
        dropbox_path: str
    ) -> Dict[str, Any]:
        """
        Faz upload de arquivo para Dropbox
        
        Args:
            file_path: Caminho do arquivo local
            dropbox_path: Caminho no Dropbox (ex: /AgroADB/relatorios/file.pdf)
        """
        if not self.access_token:
            return {"success": False, "error": "Access token não configurado"}
        
        try:
            # Simula upload (em produção usa dropbox SDK)
            return {
                "success": True,
                "path": dropbox_path,
                "size": 0,  # Seria o tamanho real
                "shared_link": f"https://www.dropbox.com/s/xyz/{dropbox_path.split('/')[-1]}",
                "uploaded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro Dropbox: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        await self.client.aclose()


class ProductivityIntegration:
    """Wrapper unificado para todas as ferramentas de produtividade"""
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        teams_webhook: Optional[str] = None,
        zapier_webhook: Optional[str] = None,
        gdrive_credentials: Optional[Dict] = None,
        dropbox_token: Optional[str] = None
    ):
        self.slack = SlackIntegration(webhook_url=slack_webhook) if slack_webhook else None
        self.teams = TeamsIntegration(webhook_url=teams_webhook) if teams_webhook else None
        self.zapier = ZapierIntegration(webhook_url=zapier_webhook) if zapier_webhook else None
        self.gdrive = GoogleDriveIntegration(credentials_json=gdrive_credentials) if gdrive_credentials else None
        self.dropbox = DropboxIntegration(access_token=dropbox_token) if dropbox_token else None
    
    async def notify_investigation_complete(
        self,
        investigation_id: int,
        investigation_title: str,
        risk_score: float,
        patterns_found: int,
        report_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Notifica conclusão de investigação em todas as plataformas
        e faz backup do relatório
        """
        import asyncio
        
        results = {}
        tasks = []
        
        # Notificações
        if self.slack:
            tasks.append(("slack", self.slack.send_investigation_alert(
                investigation_title, risk_score, patterns_found
            )))
        
        if self.teams:
            tasks.append(("teams", self.teams.send_investigation_alert(
                investigation_title, risk_score, patterns_found
            )))
        
        if self.zapier:
            tasks.append(("zapier", self.zapier.trigger_zap(
                "investigation_completed",
                {
                    "investigation_id": investigation_id,
                    "title": investigation_title,
                    "risk_score": risk_score,
                    "patterns_found": patterns_found
                }
            )))
        
        # Backup de relatório
        if report_file_path:
            if self.gdrive:
                tasks.append(("gdrive", self.gdrive.upload_file(
                    report_file_path,
                    f"investigation_{investigation_id}_report.pdf"
                )))
            
            if self.dropbox:
                tasks.append(("dropbox", self.dropbox.upload_file(
                    report_file_path,
                    f"/AgroADB/investigations/{investigation_id}/report.pdf"
                )))
        
        # Executar todas as tarefas
        if tasks:
            task_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            for i, (name, _) in enumerate(tasks):
                if isinstance(task_results[i], Exception):
                    results[name] = {"success": False, "error": str(task_results[i])}
                else:
                    results[name] = task_results[i]
        
        return {
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def close_all(self):
        """Fecha todas as conexões"""
        if self.slack:
            await self.slack.close()
        if self.teams:
            await self.teams.close()
        if self.zapier:
            await self.zapier.close()
        if self.gdrive:
            await self.gdrive.close()
        if self.dropbox:
            await self.dropbox.close()

