"""
Tests for Legal Integration Service
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.domain.investigation import InvestigationStatus
from app.domain.user import User
from app.repositories.investigation import InvestigationRepository
from app.repositories.legal_query import LegalQueryRepository
from app.services.legal_integration import (
    DueDiligenceService,
    LegalIntegrationService,
    PJeCase,
    PJeService,
)


class TestPJeService:
    """Test PJe integration service"""

    @pytest.fixture
    def pje_service(self):
        """Create PJe service instance"""
        return PJeService()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_consultar_processo_success(self, mock_get, pje_service: PJeService):
        """Test successful process query"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "numero_processo": "0000000-00.0000.0.00.0000",
            "tribunal": "TRT2",
            "classe": "Reclamação Trabalhista",
            "assunto": "Adicional de Periculosidade",
            "partes": [],
            "movimentacoes": [],
        }
        mock_get.return_value = mock_response

        result = await pje_service.consultar_processo("0000000-00.0000.0.00.0000", "TRT2")

        assert result is not None
        assert isinstance(result, PJeCase)
        assert result.numero_processo == "0000000-00.0000.0.00.0000"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_consultar_processo_not_found(self, mock_get, pje_service: PJeService):
        """Test process not found"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = await pje_service.consultar_processo("0000000-00.0000.0.00.0000", "TRT2")

        assert result is None

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_consultar_processos_parte(self, mock_get, pje_service: PJeService):
        """Test querying processes by party"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "processos": [
                {
                    "numero_processo": "0000001-00.0000.0.00.0000",
                    "tribunal": "TRT2",
                    "classe": "Reclamação Trabalhista",
                    "partes": [],
                    "movimentacoes": [],
                },
                {
                    "numero_processo": "0000002-00.0000.0.00.0000",
                    "tribunal": "TRT2",
                    "classe": "Reclamação Trabalhista",
                    "partes": [],
                    "movimentacoes": [],
                },
            ]
        }
        mock_get.return_value = mock_response

        results = await pje_service.consultar_processos_parte("12.345.678/0001-90", "qualquer")

        assert len(results) == 2
        assert all(isinstance(p, PJeCase) for p in results)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_obter_movimentacoes(self, mock_get, pje_service: PJeService):
        """Test getting process movements"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "movimentacoes": [
                {"data": "2026-02-01", "tipo": "Distribuição", "descricao": "Processo distribuído"},
                {"data": "2026-02-03", "tipo": "Despacho", "descricao": "Cite-se o réu"},
            ]
        }
        mock_get.return_value = mock_response

        results = await pje_service.obter_movimentacoes("0000000-00.0000.0.00.0000")

        assert len(results) == 2
        assert results[0]["tipo"] == "Distribuição"


class TestDueDiligenceService:
    """Test due diligence service"""

    @pytest.fixture
    def dd_service(self):
        """Create due diligence service instance"""
        return DueDiligenceService()

    @pytest.mark.asyncio
    async def test_gerar_relatorio_completo(
        self,
        dd_service: DueDiligenceService,
    ):
        """Test generating complete report from investigation data (mocked DB)."""
        inv = MagicMock()
        inv.id = 1
        inv.target_name = "Alvo Teste"
        inv.target_cpf_cnpj = "12345678901"
        inv.status = InvestigationStatus.COMPLETED
        inv.completed_at = None
        inv.properties = []
        inv.companies = []

        mock_db = AsyncMock(spec=AsyncSession)
        with patch.object(
            InvestigationRepository, "get_with_relations", new_callable=AsyncMock
        ) as m_inv:
            m_inv.return_value = inv
            with patch.object(
                LegalQueryRepository, "list_by_investigation", new_callable=AsyncMock
            ) as m_lq:
                m_lq.return_value = []
                report = await dd_service.gerar_relatorio_completo(mock_db, 1)

        assert report is not None
        assert report.investigation_id == 1
        assert "executive_summary" in report.model_dump()
        assert "risk_analysis" in report.model_dump()
        assert "financial_data" in report.model_dump()
        assert "legal_data" in report.model_dump()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_exportar_para_sistema(
        self,
        mock_post,
        dd_service: DueDiligenceService,
    ):
        """Test exporting to external system"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        inv = MagicMock()
        inv.id = 1
        inv.target_name = "Alvo"
        inv.target_cpf_cnpj = None
        inv.status = InvestigationStatus.PENDING
        inv.completed_at = None
        inv.properties = []
        inv.companies = []
        mock_db = AsyncMock(spec=AsyncSession)
        with patch.object(
            InvestigationRepository, "get_with_relations", new_callable=AsyncMock
        ) as m_inv:
            m_inv.return_value = inv
            with patch.object(
                LegalQueryRepository, "list_by_investigation", new_callable=AsyncMock
            ) as m_lq:
                m_lq.return_value = []
                report = await dd_service.gerar_relatorio_completo(mock_db, 1)

        from app.services.legal_integration import LegalSystemIntegration

        integration = LegalSystemIntegration(
            system_name="Test System",
            api_endpoint="https://api.test.com/dd",
            api_key="test-key",
            enabled=True,
        )

        result = await dd_service.exportar_para_sistema(report, integration)

        assert result is True


class TestLegalIntegrationService:
    """Test legal integration service"""

    @pytest.fixture
    def legal_service(self):
        """Create legal integration service instance"""
        return LegalIntegrationService()

    @pytest.mark.asyncio
    @patch.object(PJeService, "consultar_processos_parte")
    async def test_sincronizar_processos(
        self,
        mock_consultar,
        legal_service: LegalIntegrationService,
    ):
        """Test synchronizing processes"""
        mock_consultar.return_value = [
            PJeCase(
                numero_processo="0000001-00.0000.0.00.0000",
                tribunal="TRT2",
                partes=[],
                movimentacoes=[],
            )
        ]

        result = await legal_service.sincronizar_processos(
            db=AsyncMock(spec=AsyncSession),
            cpf_cnpj="12.345.678/0001-90",
            investigation_id=1,
        )

        assert result["success"] is True
        assert result["total_processos"] == 1

    @pytest.mark.asyncio
    @patch.object(DueDiligenceService, "gerar_relatorio_completo", new_callable=AsyncMock)
    async def test_gerar_e_exportar_due_diligence(
        self,
        mock_gerar,
        legal_service: LegalIntegrationService,
    ):
        """Test generating and exporting due diligence"""
        from app.services.legal_integration import DueDiligenceExport

        mock_report = DueDiligenceExport(
            investigation_id=1,
            target_name="Test Company",
            target_document="12.345.678/0001-90",
            executive_summary={},
            risk_analysis={},
            financial_data={},
            legal_data={},
            properties=[],
            companies=[],
            red_flags=[],
        )
        mock_gerar.return_value = mock_report

        result = await legal_service.gerar_e_exportar_due_diligence(
            db=AsyncMock(spec=AsyncSession), investigation_id=1, target_system=None
        )

        assert result["success"] is True
        assert result["report_generated"] is True
