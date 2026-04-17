"""
Tests for Conecta auth helpers
"""
import pytest

from app.services.conecta_auth import ConectaAuthService, ConectaCredentials


@pytest.mark.asyncio
async def test_conecta_auth_apikey_header():
    credentials = ConectaCredentials(
        base_url="https://conecta.gov.br",
        client_id="",
        client_secret="",
        api_key="test-api-key",
    )
    auth = ConectaAuthService(credentials, token_url="https://conecta.gov.br/oauth/token")
    headers = await auth.build_headers()
    assert headers["Authorization"] == "APIKey test-api-key"


@pytest.mark.asyncio
async def test_conecta_auth_missing_oauth():
    credentials = ConectaCredentials(
        base_url="https://conecta.gov.br",
        client_id="",
        client_secret="",
        api_key="",
    )
    auth = ConectaAuthService(credentials, token_url="https://conecta.gov.br/oauth/token")
    with pytest.raises(ValueError):
        await auth.get_access_token()


@pytest.mark.asyncio
async def test_conecta_auth_has_credentials():
    credentials_with_key = ConectaCredentials(
        base_url="https://conecta.gov.br",
        client_id="",
        client_secret="",
        api_key="key",
    )
    auth_key = ConectaAuthService(credentials_with_key, token_url="https://conecta.gov.br/oauth/token")
    assert auth_key.has_credentials() is True
    assert auth_key.has_api_key() is True

    credentials_empty = ConectaCredentials(
        base_url="https://conecta.gov.br",
        client_id="",
        client_secret="",
        api_key="",
    )
    auth_empty = ConectaAuthService(credentials_empty, token_url="https://conecta.gov.br/oauth/token")
    assert auth_empty.has_credentials() is False


@pytest.mark.asyncio
async def test_conecta_auth_build_headers_raises_when_no_credentials():
    credentials = ConectaCredentials(
        base_url="https://conecta.gov.br",
        client_id="",
        client_secret="",
        api_key="",
    )
    auth = ConectaAuthService(credentials, token_url="https://conecta.gov.br/oauth/token")
    with pytest.raises(ValueError) as exc_info:
        await auth.build_headers()
    assert "Credenciais Conecta não configuradas" in str(exc_info.value)
