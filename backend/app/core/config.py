"""
Application Configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    PROJECT_NAME: str = "AgroADB"
    PROJECT_DESCRIPTION: str = "Sistema de Inteligência Patrimonial para o Agronegócio"
    VERSION: str = "1.0.0"
    
    # Environment
    ENVIRONMENT: str = "development"
    ENABLE_WORKERS: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = ""  # Para criptografia de dados sensíveis
    
    # HTTPS
    FORCE_HTTPS: bool = False  # True em produção
    HTTPS_REDIRECT: bool = False  # True em produção
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_MAX_AGE: int = 600  # 10 minutos
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Scraping
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_MAX_RETRIES: int = 3
    SCRAPING_DELAY: float = 1.0
    
    # External APIs (opcional - adicionar conforme necessário)
    INCRA_API_KEY: str = ""
    CAR_API_KEY: str = ""
    SERPAPI_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Legal Integration APIs
    PJE_API_URL: str = ""
    PJE_API_KEY: str = ""
    
    # Tribunais Estaduais - e-SAJ e Projudi (não requer API key - web scraping)
    ESAJ_ENABLED: bool = True
    PROJUDI_ENABLED: bool = True
    
    # Birôs de Crédito
    # SERASA EXPERIAN
    SERASA_API_KEY: str = ""
    SERASA_CLIENT_ID: str = ""
    SERASA_CLIENT_SECRET: str = ""
    
    # BOA VISTA SCPC
    BOAVISTA_API_KEY: str = ""
    BOAVISTA_CLIENT_ID: str = ""
    BOAVISTA_CLIENT_SECRET: str = ""

    # DataJud (CNJ)
    DATAJUD_API_URL: str = "https://api-publica.datajud.cnj.jus.br"
    DATAJUD_API_KEY: str = ""

    # Conecta gov.br - SNCR
    CONECTA_SNCR_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_SNCR_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_SNCR_CLIENT_ID: str = ""
    CONECTA_SNCR_CLIENT_SECRET: str = ""
    CONECTA_SNCR_API_KEY: str = ""
    CONECTA_SNCR_IMOVEL_PATH: str = "/api-sncr/v2/consultarImovelPorCodigo/{codigo}"
    CONECTA_SNCR_CPF_CNPJ_PATH: str = "/api-sncr/v2/consultarImovelPorCpfCnpj/{cpf_cnpj}"
    CONECTA_SNCR_SITUACAO_PATH: str = "/api-sncr/v2/verificarSituacaoImovel/{codigo}"
    CONECTA_SNCR_CCIR_PATH: str = "/api-sncr/v2/baixarCcirPorCodigoImovel/{codigo}"

    # Conecta gov.br - SIGEF
    CONECTA_SIGEF_API_URL: str = ""
    CONECTA_SIGEF_TOKEN_URL: str = ""
    CONECTA_SIGEF_CLIENT_ID: str = ""
    CONECTA_SIGEF_CLIENT_SECRET: str = ""
    CONECTA_SIGEF_API_KEY: str = ""
    CONECTA_SIGEF_IMOVEL_PATH: str = ""
    CONECTA_SIGEF_PARCELAS_PATH: str = ""
    CONECTA_SIGEF_SCOPES: str = ""

    # Conecta gov.br - SICAR
    CONECTA_SICAR_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_SICAR_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_SICAR_CLIENT_ID: str = ""
    CONECTA_SICAR_CLIENT_SECRET: str = ""
    CONECTA_SICAR_API_KEY: str = ""
    CONECTA_SICAR_CPF_CNPJ_PATH: str = "/api-sicar-cpfcnpj/v1/{cpf_cnpj}"
    CONECTA_SICAR_IMOVEL_PATH: str = ""

    # Conecta gov.br - SNCCI
    CONECTA_SNCCI_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_SNCCI_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_SNCCI_CLIENT_ID: str = ""
    CONECTA_SNCCI_CLIENT_SECRET: str = ""
    CONECTA_SNCCI_API_KEY: str = ""
    CONECTA_SNCCI_PARCELAS_PATH: str = "/sncci/v1/parcelas"
    CONECTA_SNCCI_CREDITOS_ATIVOS_PATH: str = "/sncci/v1/creditos-ativos"
    CONECTA_SNCCI_CREDITOS_PATH: str = "/sncci/v1/creditos/{codigo}"
    CONECTA_SNCCI_BOLETOS_PATH: str = "/sncci/v1/boletos"

    # Conecta gov.br - SIGEF GEO
    CONECTA_SIGEF_GEO_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_SIGEF_GEO_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_SIGEF_GEO_CLIENT_ID: str = ""
    CONECTA_SIGEF_GEO_CLIENT_SECRET: str = ""
    CONECTA_SIGEF_GEO_API_KEY: str = ""
    CONECTA_SIGEF_GEO_PARCELAS_PATH: str = "/api-sigef-geo/v1/parcelas"
    CONECTA_SIGEF_GEO_PARCELAS_GEOJSON_PATH: str = "/api-sigef-geo/v1/parcelas/serpro"

    # Conecta gov.br - Consulta CNPJ (RFB)
    CONECTA_CNPJ_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_CNPJ_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_CNPJ_CLIENT_ID: str = ""
    CONECTA_CNPJ_CLIENT_SECRET: str = ""
    CONECTA_CNPJ_API_KEY: str = ""
    CONECTA_CNPJ_BASICA_PATH: str = "/api-cnpj-basica/v2/basica/{cnpj}"
    CONECTA_CNPJ_QSA_PATH: str = "/api-cnpj-qsa/v2/qsa/{cnpj}"
    CONECTA_CNPJ_EMPRESA_PATH: str = "/api-cnpj-empresa/v2/empresa/{cnpj}"

    # Conecta gov.br - Consulta CND (RFB/PGFN)
    CONECTA_CND_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_CND_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_CND_CLIENT_ID: str = ""
    CONECTA_CND_CLIENT_SECRET: str = ""
    CONECTA_CND_API_KEY: str = ""
    CONECTA_CND_CERTIDAO_PATH: str = "/api-cnd/v1/ConsultaCnd/certidao"

    # Conecta gov.br - CADIN Consulta/Contratante
    CONECTA_CADIN_API_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br"
    CONECTA_CADIN_TOKEN_URL: str = "https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token"
    CONECTA_CADIN_CLIENT_ID: str = ""
    CONECTA_CADIN_CLIENT_SECRET: str = ""
    CONECTA_CADIN_API_KEY: str = ""
    CONECTA_CADIN_INFO_CPF_PATH: str = "/registro/info/{cpf}/cpf"
    CONECTA_CADIN_INFO_CNPJ_PATH: str = "/registro/info/{cnpj}/cnpj"
    CONECTA_CADIN_COMPLETA_CPF_PATH: str = "/registro/consultaCompleta/{cpf}/cpf"
    CONECTA_CADIN_COMPLETA_CNPJ_PATH: str = "/registro/consultaCompleta/{cnpj}/cnpj"
    CONECTA_CADIN_VERSAO_PATH: str = "/registro/versaoApi"

    # Portal gov.br - API de Serviços
    PORTAL_SERVICOS_API_URL: str = "https://www.servicos.gov.br/api/v1"
    PORTAL_SERVICOS_AUTH_TOKEN: str = ""

    # Portal gov.br - API de Serviços Estaduais
    SERVICOS_ESTADUAIS_API_URL: str = "https://gov.br/apiestados"
    SERVICOS_ESTADUAIS_AUTH_TOKEN: str = ""

    # SIGEF / INCRA Parcelas (Infosimples ou WS similar)
    SIGEF_PARCELAS_API_URL: str = ""
    SIGEF_PARCELAS_MAX_PAGES: int = 5
    SIGEF_LOGIN_CPF: str = ""
    SIGEF_LOGIN_SENHA: str = ""
    SIGEF_PKCS12_CERT: str = ""
    SIGEF_PKCS12_PASS: str = ""

    # Portal da Transparência (CGU) — API Key gratuita
    PORTAL_TRANSPARENCIA_API_KEY: str = ""
    
    # SMTP / Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@agroadb.com"
    SMTP_FROM_NAME: str = "AgroADB Platform"
    
    # Frontend URL (para links em emails)
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Celery / Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
