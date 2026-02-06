"""
Integração com Ferramentas Jurídicas
Sistema de integração com APIs e sistemas jurídicos
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import httpx
from app.core.config import settings

# ==================== Models ====================

class PJeCase(BaseModel):
    """Modelo para processo no PJe"""
    numero_processo: str = Field(..., description="Número do processo CNJ")
    tribunal: str = Field(..., description="Tribunal de origem")
    classe: Optional[str] = None
    assunto: Optional[str] = None
    area: Optional[str] = None
    valor_causa: Optional[float] = None
    data_distribuicao: Optional[datetime] = None
    partes: List[Dict[str, str]] = Field(default_factory=list)
    movimentacoes: List[Dict[str, Any]] = Field(default_factory=list)

class DueDiligenceExport(BaseModel):
    """Modelo para exportação de due diligence"""
    investigation_id: int
    target_name: str
    target_document: str
    executive_summary: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    financial_data: Dict[str, Any]
    legal_data: Dict[str, Any]
    properties: List[Dict[str, Any]]
    companies: List[Dict[str, Any]]
    red_flags: List[str]

class LegalSystemIntegration(BaseModel):
    """Modelo para integração com sistema jurídico"""
    system_name: str
    api_endpoint: str
    api_key: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    enabled: bool = True

# ==================== Serviço de Integração com PJe ====================

class PJeService:
    """Serviço para integração com o Processo Judicial Eletrônico (PJe)"""
    
    def __init__(self):
        self.base_url = settings.PJE_API_URL or "https://api.pje.jus.br"
        self.api_key = settings.PJE_API_KEY
        self.timeout = 30.0
    
    async def consultar_processo(self, numero_processo: str, tribunal: str) -> Optional[PJeCase]:
        """
        Consulta um processo no PJe
        
        Args:
            numero_processo: Número do processo no formato CNJ
            tribunal: Código do tribunal (ex: TRT2, TST, STJ)
        
        Returns:
            Dados do processo ou None se não encontrado
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/processos/{numero_processo}",
                    params={"tribunal": tribunal},
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return PJeCase(**data)
                elif response.status_code == 404:
                    return None
                else:
                    raise Exception(f"Erro ao consultar PJe: {response.status_code}")
        
        except httpx.TimeoutException:
            raise Exception("Timeout ao consultar PJe")
        except Exception as e:
            raise Exception(f"Erro na integração com PJe: {str(e)}")
    
    async def consultar_processos_parte(
        self, 
        cpf_cnpj: str, 
        tipo_parte: str = "qualquer"
    ) -> List[PJeCase]:
        """
        Consulta processos de uma parte (autor, réu, etc)
        
        Args:
            cpf_cnpj: CPF ou CNPJ da parte
            tipo_parte: Tipo de participação (autor, reu, qualquer)
        
        Returns:
            Lista de processos encontrados
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/processos/parte",
                    params={
                        "documento": cpf_cnpj,
                        "tipo": tipo_parte
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [PJeCase(**processo) for processo in data.get("processos", [])]
                else:
                    return []
        
        except Exception as e:
            raise Exception(f"Erro ao consultar processos por parte: {str(e)}")
    
    async def obter_movimentacoes(self, numero_processo: str) -> List[Dict[str, Any]]:
        """
        Obtém as movimentações de um processo
        
        Args:
            numero_processo: Número do processo
        
        Returns:
            Lista de movimentações
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/processos/{numero_processo}/movimentacoes",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("movimentacoes", [])
                else:
                    return []
        
        except Exception as e:
            raise Exception(f"Erro ao obter movimentações: {str(e)}")

# ==================== Serviço de Due Diligence ====================

class DueDiligenceService:
    """Serviço para exportação de relatórios de due diligence"""
    
    @staticmethod
    async def gerar_relatorio_completo(
        db: Session, 
        investigation_id: int
    ) -> DueDiligenceExport:
        """
        Gera relatório completo de due diligence
        
        Args:
            db: Sessão do banco de dados
            investigation_id: ID da investigação
        
        Returns:
            Relatório de due diligence estruturado
        """
        # TODO: Buscar dados reais da investigação
        # investigation = db.query(Investigation).filter_by(id=investigation_id).first()
        
        # Simulação para exemplo
        report = DueDiligenceExport(
            investigation_id=investigation_id,
            target_name="Fazenda São João Ltda",
            target_document="12.345.678/0001-90",
            executive_summary={
                "status": "Concluída",
                "risk_level": "Médio",
                "total_properties": 15,
                "total_companies": 3,
                "red_flags_count": 4,
                "completion_date": datetime.now().isoformat()
            },
            risk_analysis={
                "overall_risk": "medium",
                "financial_risk": "low",
                "legal_risk": "high",
                "operational_risk": "medium",
                "factors": [
                    "Processos trabalhistas ativos",
                    "Propriedades com pendências ambientais",
                    "Boa saúde financeira"
                ]
            },
            financial_data={
                "total_assets": 25000000.00,
                "total_liabilities": 8500000.00,
                "net_worth": 16500000.00,
                "revenue_last_year": 12000000.00
            },
            legal_data={
                "active_lawsuits": 12,
                "environmental_issues": 3,
                "labor_lawsuits": 5,
                "tax_issues": 2
            },
            properties=[
                {
                    "matricula": "12345",
                    "area": 500.0,
                    "estado": "SP",
                    "municipio": "Ribeirão Preto",
                    "valor_estimado": 5000000.00
                }
            ],
            companies=[
                {
                    "cnpj": "12.345.678/0001-90",
                    "razao_social": "Fazenda São João Ltda",
                    "capital_social": 1000000.00
                }
            ],
            red_flags=[
                "⚠️ Processos trabalhistas com alto valor de causa",
                "⚠️ Embargo ambiental em propriedade",
                "⚠️ Certidão negativa de débitos vencida",
                "⚠️ Sócio com restrições no CPF"
            ]
        )
        
        return report
    
    @staticmethod
    async def exportar_para_sistema(
        report: DueDiligenceExport,
        system_integration: LegalSystemIntegration
    ) -> bool:
        """
        Exporta relatório para sistema jurídico externo
        
        Args:
            report: Relatório de due diligence
            system_integration: Configuração da integração
        
        Returns:
            True se exportado com sucesso
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = report.dict()
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                if system_integration.api_key:
                    headers["Authorization"] = f"Bearer {system_integration.api_key}"
                
                response = await client.post(
                    system_integration.api_endpoint,
                    json=payload,
                    headers=headers
                )
                
                return response.status_code in [200, 201]
        
        except Exception as e:
            raise Exception(f"Erro ao exportar para sistema: {str(e)}")

# ==================== Serviço de Integração Geral ====================

class LegalIntegrationService:
    """Serviço geral de integração com ferramentas jurídicas"""
    
    def __init__(self):
        self.pje_service = PJeService()
        self.due_diligence_service = DueDiligenceService()
    
    async def sincronizar_processos(
        self, 
        db: Session, 
        cpf_cnpj: str,
        investigation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sincroniza processos judiciais de uma parte
        
        Args:
            db: Sessão do banco de dados
            cpf_cnpj: CPF ou CNPJ para consulta
            investigation_id: ID da investigação (opcional)
        
        Returns:
            Resultado da sincronização
        """
        try:
            # Consultar processos no PJe
            processos = await self.pje_service.consultar_processos_parte(cpf_cnpj)
            
            # TODO: Salvar processos no banco de dados
            # for processo in processos:
            #     db_processo = JudicialProcess(**processo.dict())
            #     db.add(db_processo)
            # db.commit()
            
            return {
                "success": True,
                "total_processos": len(processos),
                "processos": [p.dict() for p in processos],
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def gerar_e_exportar_due_diligence(
        self,
        db: Session,
        investigation_id: int,
        target_system: Optional[LegalSystemIntegration] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório de due diligence e exporta para sistema externo
        
        Args:
            db: Sessão do banco de dados
            investigation_id: ID da investigação
            target_system: Sistema alvo para exportação (opcional)
        
        Returns:
            Resultado da operação
        """
        try:
            # Gerar relatório
            report = await self.due_diligence_service.gerar_relatorio_completo(
                db, investigation_id
            )
            
            result = {
                "success": True,
                "report_generated": True,
                "investigation_id": investigation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Exportar se sistema alvo fornecido
            if target_system and target_system.enabled:
                exported = await self.due_diligence_service.exportar_para_sistema(
                    report, target_system
                )
                result["exported"] = exported
                result["target_system"] = target_system.system_name
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global
legal_integration_service = LegalIntegrationService()
