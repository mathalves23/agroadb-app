"""
Testes para serviços de integração legal: DataJud, SIGEF Parcelas, Conecta (SNCR).
Usa mock de httpx para não depender de APIs externas.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_datajud_service_raises_when_api_key_missing():
    with patch.dict("app.services.datajud.settings.__dict__", {"DATAJUD_API_URL": "https://api.datajud.cnj.jus.br", "DATAJUD_API_KEY": ""}):
        from app.services.datajud import DataJudService
        service = DataJudService()
        with pytest.raises(ValueError) as exc_info:
            await service.request("GET", "/test")
        assert "DATAJUD_API_KEY" in str(exc_info.value)


@pytest.mark.asyncio
async def test_datajud_service_request_success():
    with patch.dict("app.services.datajud.settings.__dict__", {"DATAJUD_API_URL": "https://api.datajud.cnj.jus.br", "DATAJUD_API_KEY": "test-key"}):
        from app.services.datajud import DataJudService
        service = DataJudService()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"hits": [], "total": 0}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await service.request("GET", "/tribunais/TRT2/_search")
            assert result == {"hits": [], "total": 0}


@pytest.mark.asyncio
async def test_sigef_parcelas_service_raises_when_url_not_configured():
    with patch.dict("app.services.sigef_parcelas.settings.__dict__", {"SIGEF_PARCELAS_API_URL": "", "SIGEF_PARCELAS_MAX_PAGES": 5}):
        from app.services.sigef_parcelas import SigefParcelasService
        service = SigefParcelasService()
        with pytest.raises(ValueError) as exc_info:
            await service.query({})
        assert "SIGEF_PARCELAS_API_URL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_sigef_parcelas_service_query_success():
    with patch.dict("app.services.sigef_parcelas.settings.__dict__", {"SIGEF_PARCELAS_API_URL": "https://sigef.example.com/parcelas", "SIGEF_PARCELAS_MAX_PAGES": 5}):
        from app.services.sigef_parcelas import SigefParcelasService
        service = SigefParcelasService()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"parcelas": [], "total": 0}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await service.query({"cpf": "12345678900", "pagina": 1})
            assert "parcelas" in result
            assert result["total"] == 0


@pytest.mark.asyncio
async def test_conecta_sncr_raises_when_credentials_missing():
    with patch("app.services.conecta_sncr.settings") as mock_settings:
        mock_settings.CONECTA_SNCR_API_URL = "https://conecta.gov.br"
        mock_settings.CONECTA_SNCR_IMOVEL_PATH = "/api-sncr/v2/imovel/{codigo}"
        mock_settings.CONECTA_SNCR_CPF_CNPJ_PATH = "/api-sncr/v2/cpf/{cpf_cnpj}"
        mock_settings.CONECTA_SNCR_SITUACAO_PATH = "/api-sncr/v2/situacao/{codigo}"
        mock_settings.CONECTA_SNCR_CCIR_PATH = "/api-sncr/v2/ccir/{codigo}"
        mock_settings.CONECTA_SNCR_TOKEN_URL = "https://conecta.gov.br/token"
        mock_settings.CONECTA_SNCR_CLIENT_ID = ""
        mock_settings.CONECTA_SNCR_CLIENT_SECRET = ""
        mock_settings.CONECTA_SNCR_API_KEY = ""

        from app.services.conecta_sncr import ConectaSNCRService
        service = ConectaSNCRService()
        with pytest.raises(ValueError) as exc_info:
            await service.consultar_imovel("12345")
        assert "Credenciais Conecta SNCR" in str(exc_info.value)
