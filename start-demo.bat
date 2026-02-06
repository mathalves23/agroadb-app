@echo off
chcp 65001 >nul
cls

echo ═══════════════════════════════════════════════════════════════════
echo   🚀 AgroADB - DEMO RÁPIDA
echo ═══════════════════════════════════════════════════════════════════
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.11+ primeiro.
    echo    Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado! Instale Node.js 18+ primeiro.
    echo    Download: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados
echo.

:: ═══════════════════════════════════════════════════════════════════
:: BACKEND
:: ═══════════════════════════════════════════════════════════════════
echo ═══════════════════════════════════════════════════════════════════
echo   📦 CONFIGURANDO BACKEND
echo ═══════════════════════════════════════════════════════════════════
echo.

cd backend

:: Criar ambiente virtual
if not exist "venv" (
    echo 📝 Criando ambiente virtual...
    python -m venv venv
)

:: Ativar ambiente virtual
call venv\Scripts\activate.bat

:: Instalar dependências
echo 📦 Instalando dependências do backend...
pip install -q -r requirements.txt

:: Criar arquivo .env se não existir
if not exist ".env" (
    echo 📝 Criando configuração (.env^)...
    (
        echo DATABASE_URL=sqlite:///./agroadb.db
        echo REDIS_URL=redis://localhost:6379/0
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo ENVIRONMENT=development
    ) > .env
)

:: Criar banco de dados
echo 🗄️  Criando banco de dados...
python -c "from app.core.database import create_tables; import asyncio; asyncio.run(create_tables())" 2>nul

:: Popular com dados demo
echo 🎬 Criando dados de demonstração...
echo.
python -m scripts.seed_demo_data
echo.

:: Iniciar backend em background
echo 🚀 Iniciando backend na porta 8000...
start /B cmd /c "venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1"

cd ..

:: ═══════════════════════════════════════════════════════════════════
:: FRONTEND
:: ═══════════════════════════════════════════════════════════════════
echo ═══════════════════════════════════════════════════════════════════
echo   🎨 CONFIGURANDO FRONTEND
echo ═══════════════════════════════════════════════════════════════════
echo.

cd frontend

:: Instalar dependências
if not exist "node_modules" (
    echo 📦 Instalando dependências do frontend...
    call npm install --silent
) else (
    echo ✅ Dependências do frontend já instaladas
)

:: Iniciar frontend
echo 🚀 Iniciando frontend na porta 5173...
echo.
start cmd /k "npm run dev"

cd ..

:: ═══════════════════════════════════════════════════════════════════
:: FINALIZAÇÃO
:: ═══════════════════════════════════════════════════════════════════
timeout /t 5 /nobreak >nul

cls
echo ═══════════════════════════════════════════════════════════════════
echo   ✅ AgroADB DEMO INICIADA COM SUCESSO!
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 🌐 ACESSE A APLICAÇÃO:
echo    http://localhost:5173
echo.
echo 🔐 CREDENCIAIS DE TESTE:
echo.
echo    👤 Usuário 1 (Principal):
echo       Email: demo@agroadb.com
echo       Senha: demo123
echo.
echo    👤 Usuário 2:
echo       Email: maria.silva@agroadb.com
echo       Senha: demo123
echo.
echo    👤 Usuário 3:
echo       Email: joao.santos@agroadb.com
echo       Senha: demo123
echo.
echo 📊 DADOS DISPONÍVEIS:
echo    ✓ Múltiplos usuários e investigações
echo    ✓ Propriedades rurais
echo    ✓ Empresas e contratos
echo    ✓ Notificações e comentários
echo.
echo ⚙️  BACKEND API:
echo    http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.
echo ═══════════════════════════════════════════════════════════════════
echo   Para PARAR a aplicação: Feche as janelas ou pressione Ctrl+C
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
