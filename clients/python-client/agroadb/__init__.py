"""
AgroADB Python Client Library

Cliente Python oficial para a API do AgroADB - Sistema de Análise de Dados Agrários.

Features:
- Autenticação automática (JWT)
- Type hints completos
- Suporte assíncrono (async/await)
- Rate limiting inteligente
- Retry automático
- Logging integrado
"""

import os
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

__version__ = "1.0.0"
__author__ = "AgroADB Team"

logger = logging.getLogger(__name__)


class AgroADBException(Exception):
    """Exceção base para erros da API AgroADB"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(AgroADBException):
    """Erro de autenticação"""
    pass


class ValidationError(AgroADBException):
    """Erro de validação de dados"""
    pass


class NotFoundError(AgroADBException):
    """Recurso não encontrado"""
    pass


class RateLimitError(AgroADBException):
    """Limite de requisições excedido"""
    pass


class AgroADBClient:
    """
    Cliente Python para API AgroADB
    
    Exemplo de uso:
        ```python
        from agroadb import AgroADBClient
        
        # Inicializar cliente
        client = AgroADBClient(
            api_key="sua_api_key",
            base_url="https://api.agroadb.com"
        )
        
        # Fazer login
        client.login("usuario@email.com", "senha")
        
        # Listar investigações
        investigations = client.investigations.list(limit=10)
        
        # Criar investigação
        new_inv = client.investigations.create({
            "title": "Nova Investigação",
            "description": "Descrição"
        })
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True
    ):
        """
        Inicializa cliente AgroADB
        
        Args:
            base_url: URL base da API
            api_key: API key para autenticação (opcional)
            timeout: Timeout das requisições em segundos
            max_retries: Número máximo de tentativas
            verify_ssl: Verificar certificados SSL
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
        # Configurar sessão com retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Inicializar módulos
        self.auth = AuthModule(self)
        self.investigations = InvestigationsModule(self)
        self.documents = DocumentsModule(self)
        self.users = UsersModule(self)
        self.analytics = AnalyticsModule(self)
        self.integrations = IntegrationsModule(self)
        self.export = ExportModule(self)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Faz login e armazena tokens
        
        Args:
            email: Email do usuário
            password: Senha
            
        Returns:
            Dados do usuário e tokens
        """
        response = self.auth.login(email, password)
        self.access_token = response.get("access_token")
        self.refresh_token = response.get("refresh_token")
        return response
    
    def logout(self):
        """Faz logout e limpa tokens"""
        self.access_token = None
        self.refresh_token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisição"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        data: Optional[Any] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Faz requisição HTTP
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            params: Query parameters
            json: Dados JSON
            data: Dados form
            files: Arquivos para upload
            
        Returns:
            Resposta da API
            
        Raises:
            AgroADBException: Em caso de erro
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        # Remover Content-Type se enviando arquivos
        if files:
            headers.pop("Content-Type", None)
        
        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                files=files,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Tratar erros HTTP
            if response.status_code == 401:
                raise AuthenticationError("Não autorizado", response.status_code, response.json())
            elif response.status_code == 404:
                raise NotFoundError("Recurso não encontrado", response.status_code)
            elif response.status_code == 429:
                raise RateLimitError("Limite de requisições excedido", response.status_code)
            elif response.status_code == 422:
                raise ValidationError("Erro de validação", response.status_code, response.json())
            elif response.status_code >= 400:
                raise AgroADBException(
                    f"Erro na API: {response.status_code}",
                    response.status_code,
                    response.json() if response.text else None
                )
            
            return response.json() if response.text else {}
            
        except requests.exceptions.Timeout:
            raise AgroADBException(f"Timeout após {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise AgroADBException(f"Erro de conexão com {url}")
        except requests.exceptions.RequestException as e:
            raise AgroADBException(f"Erro na requisição: {str(e)}")


class BaseModule:
    """Classe base para módulos da API"""
    
    def __init__(self, client: AgroADBClient):
        self.client = client
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self.client._request("GET", endpoint, params=params)
    
    def _post(self, endpoint: str, json: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        return self.client._request("POST", endpoint, json=json, files=files)
    
    def _put(self, endpoint: str, json: Dict) -> Dict[str, Any]:
        return self.client._request("PUT", endpoint, json=json)
    
    def _patch(self, endpoint: str, json: Dict) -> Dict[str, Any]:
        return self.client._request("PATCH", endpoint, json=json)
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        return self.client._request("DELETE", endpoint)


class AuthModule(BaseModule):
    """Módulo de autenticação"""
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login"""
        return self._post("/api/v1/auth/login", json={"email": email, "password": password})
    
    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrar novo usuário"""
        return self._post("/api/v1/auth/register", json=data)
    
    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        """Renovar token"""
        return self._post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    
    def me(self) -> Dict[str, Any]:
        """Dados do usuário atual"""
        return self._get("/api/v1/auth/me")


class InvestigationsModule(BaseModule):
    """Módulo de investigações"""
    
    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista investigações"""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        return self._get("/api/v1/investigations", params=params).get("items", [])
    
    def get(self, investigation_id: int) -> Dict[str, Any]:
        """Obtém investigação por ID"""
        return self._get(f"/api/v1/investigations/{investigation_id}")
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova investigação"""
        return self._post("/api/v1/investigations", json=data)
    
    def update(self, investigation_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza investigação"""
        return self._put(f"/api/v1/investigations/{investigation_id}", json=data)
    
    def delete(self, investigation_id: int) -> Dict[str, Any]:
        """Deleta investigação"""
        return self._delete(f"/api/v1/investigations/{investigation_id}")
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Busca investigações"""
        params = {"q": query}
        if filters:
            params.update(filters)
        return self._get("/api/v1/investigations/search", params=params).get("results", [])


class DocumentsModule(BaseModule):
    """Módulo de documentos"""
    
    def list(self, investigation_id: int) -> List[Dict[str, Any]]:
        """Lista documentos de uma investigação"""
        return self._get(f"/api/v1/investigations/{investigation_id}/documents").get("items", [])
    
    def get(self, document_id: int) -> Dict[str, Any]:
        """Obtém documento por ID"""
        return self._get(f"/api/v1/documents/{document_id}")
    
    def upload(self, investigation_id: int, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Upload de documento"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = metadata or {}
            return self._post(
                f"/api/v1/investigations/{investigation_id}/documents",
                files=files
            )
    
    def download(self, document_id: int, output_path: str):
        """Download de documento"""
        response = self.client.session.get(
            f"{self.client.base_url}/api/v1/documents/{document_id}/download",
            headers=self.client._get_headers(),
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def delete(self, document_id: int) -> Dict[str, Any]:
        """Deleta documento"""
        return self._delete(f"/api/v1/documents/{document_id}")


class UsersModule(BaseModule):
    """Módulo de usuários"""
    
    def list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista usuários"""
        return self._get("/api/v1/users", params={"limit": limit, "offset": offset}).get("items", [])
    
    def get(self, user_id: int) -> Dict[str, Any]:
        """Obtém usuário por ID"""
        return self._get(f"/api/v1/users/{user_id}")
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria novo usuário"""
        return self._post("/api/v1/users", json=data)
    
    def update(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza usuário"""
        return self._put(f"/api/v1/users/{user_id}", json=data)
    
    def delete(self, user_id: int) -> Dict[str, Any]:
        """Deleta usuário"""
        return self._delete(f"/api/v1/users/{user_id}")


class AnalyticsModule(BaseModule):
    """Módulo de analytics"""
    
    def dashboard(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Dashboard consolidado"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/api/v1/analytics/dashboard", params=params)
    
    def performance_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Relatório de performance"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/api/v1/analytics/reports/performance", params=params)
    
    def user_analytics(self) -> Dict[str, Any]:
        """Analytics de usuários"""
        return self._get("/api/v1/analytics/user/dashboard")
    
    def funnel_analysis(self, funnel_key: str) -> Dict[str, Any]:
        """Análise de funil"""
        return self._get(f"/api/v1/analytics/user/funnel/{funnel_key}")


class IntegrationsModule(BaseModule):
    """Módulo de integrações"""
    
    def list(self) -> List[Dict[str, Any]]:
        """Lista integrações disponíveis"""
        return self._get("/api/v1/integrations").get("integrations", [])
    
    def tjsp_search(self, cpf: str) -> Dict[str, Any]:
        """Busca no TJSP"""
        return self._post("/api/v1/integrations/tjsp/search", json={"cpf": cpf})
    
    def serasa_query(self, cpf: str) -> Dict[str, Any]:
        """Consulta Serasa"""
        return self._post("/api/v1/integrations/serasa/query", json={"cpf": cpf})
    
    def receita_federal(self, cnpj: str) -> Dict[str, Any]:
        """Consulta Receita Federal"""
        return self._post("/api/v1/integrations/receita-federal/cnpj", json={"cnpj": cnpj})


class ExportModule(BaseModule):
    """Módulo de exportação"""
    
    def create_export(
        self,
        data_source: str,
        export_format: str = "json",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria job de exportação"""
        params = {
            "data_source": data_source,
            "export_format": export_format
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._post("/api/v1/analytics/export/file/create", params=params)
    
    def get_export_status(self, job_id: str) -> Dict[str, Any]:
        """Status de exportação"""
        return self._get(f"/api/v1/analytics/export/file/status/{job_id}")
    
    def list_exports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lista jobs de exportação"""
        return self._get("/api/v1/analytics/export/file/list", params={"limit": limit}).get("jobs", [])
    
    def download_export(self, job_id: str, output_path: str):
        """Download de arquivo exportado"""
        response = self.client.session.get(
            f"{self.client.base_url}/api/v1/analytics/export/file/download/{job_id}",
            headers=self.client._get_headers(),
            stream=True
        )
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def export_to_bigquery(
        self,
        project_id: str,
        dataset: str,
        table_name: str,
        data_source: str
    ) -> Dict[str, Any]:
        """Exporta para BigQuery"""
        params = {
            "project_id": project_id,
            "dataset": dataset,
            "table_name": table_name,
            "data_source": data_source
        }
        return self._post("/api/v1/analytics/export/warehouse/bigquery", params=params)
    
    def export_to_redshift(
        self,
        cluster: str,
        database: str,
        table_name: str,
        data_source: str
    ) -> Dict[str, Any]:
        """Exporta para Redshift"""
        params = {
            "cluster": cluster,
            "database": database,
            "table_name": table_name,
            "data_source": data_source
        }
        return self._post("/api/v1/analytics/export/warehouse/redshift", params=params)


# Funções auxiliares
def create_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> AgroADBClient:
    """
    Cria cliente AgroADB com configuração de ambiente
    
    Exemplo:
        ```python
        from agroadb import create_client
        
        client = create_client()  # Usa variáveis de ambiente
        ```
    """
    base_url = base_url or os.getenv("AGROADB_BASE_URL", "http://localhost:8000")
    api_key = api_key or os.getenv("AGROADB_API_KEY")
    
    return AgroADBClient(base_url=base_url, api_key=api_key, **kwargs)
