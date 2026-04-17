# Instalação de Dependências - Integrações Web Scraping

## 📦 Dependências Python

As novas integrações com tribunais estaduais (e-SAJ e Projudi) utilizam web scraping. É necessário instalar:

### 1. BeautifulSoup4
```bash
pip install beautifulsoup4
```

### 2. Selenium
```bash
pip install selenium
```

### 3. lxml (opcional, mas recomendado para melhor performance)
```bash
pip install lxml
```

---

## 🌐 ChromeDriver (para Selenium)

O Selenium precisa do ChromeDriver para controlar o navegador Chrome.

### Opção 1: Instalação Automática (Recomendado)
```bash
pip install webdriver-manager
```

Então, no código:
```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

### Opção 2: Instalação Manual

#### Ubuntu/Debian:
```bash
# Instalar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Instalar ChromeDriver
sudo apt-get install -y chromium-driver
```

#### macOS (com Homebrew):
```bash
brew install chromedriver
```

#### Windows:
1. Baixar ChromeDriver: https://chromedriver.chromium.org/
2. Extrair para uma pasta (ex: C:\chromedriver)
3. Adicionar ao PATH

---

## 🐳 Docker

Se você usar Docker, adicione ao `backend/Dockerfile`:

```dockerfile
# Instalar Chrome e ChromeDriver para Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get install -y chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente para Chrome headless
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROME_DRIVER=/usr/bin/chromedriver
```

### docker-compose.yml

Adicione ao serviço backend:

```yaml
backend:
  # ... outras configurações
  environment:
    - CHROME_BIN=/usr/bin/google-chrome-stable
    - CHROME_DRIVER=/usr/bin/chromedriver
  shm_size: '2gb'  # Necessário para Chrome headless
```

---

## 📋 requirements.txt

Adicione ao `backend/requirements.txt`:

```txt
beautifulsoup4==4.12.2
selenium==4.16.0
webdriver-manager==4.0.1
lxml==4.9.3
```

---

## 🔧 Configuração do Chrome Headless

Para ambientes de produção sem interface gráfica:

```python
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=chrome_options)
```

---

## ✅ Verificação da Instalação

Execute este script para verificar se tudo está instalado corretamente:

```python
#!/usr/bin/env python3
"""
Verifica instalação das dependências de web scraping
"""

def check_beautifulsoup():
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup4 instalado")
        return True
    except ImportError:
        print("❌ BeautifulSoup4 não encontrado")
        print("   Instale com: pip install beautifulsoup4")
        return False


def check_selenium():
    try:
        from selenium import webdriver
        print("✅ Selenium instalado")
        return True
    except ImportError:
        print("❌ Selenium não encontrado")
        print("   Instale com: pip install selenium")
        return False


def check_chromedriver():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        
        print("✅ ChromeDriver instalado e funcionando")
        return True
    except Exception as e:
        print("❌ ChromeDriver não encontrado ou com problema")
        print(f"   Erro: {e}")
        print("   Instale conforme instruções acima")
        return False


def check_lxml():
    try:
        import lxml
        print("✅ lxml instalado")
        return True
    except ImportError:
        print("⚠️  lxml não encontrado (opcional)")
        print("   Instale com: pip install lxml")
        return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔍 VERIFICANDO DEPENDÊNCIAS DE WEB SCRAPING")
    print("="*50 + "\n")
    
    bs4_ok = check_beautifulsoup()
    selenium_ok = check_selenium()
    chromedriver_ok = check_chromedriver()
    lxml_ok = check_lxml()
    
    print("\n" + "="*50)
    
    if bs4_ok and selenium_ok and chromedriver_ok:
        print("✅ TODAS AS DEPENDÊNCIAS ESSENCIAIS INSTALADAS!")
    else:
        print("❌ ALGUMAS DEPENDÊNCIAS ESTÃO FALTANDO")
        print("   Siga as instruções acima para instalar")
    
    print("="*50 + "\n")
```

Salve como `check_dependencies.py` e execute:
```bash
python check_dependencies.py
```

---

## 🚀 Instalação Rápida (Tudo de uma vez)

### Ambiente de Desenvolvimento:

```bash
# 1. Instalar dependências Python
pip install beautifulsoup4 selenium webdriver-manager lxml

# 2. Para Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-driver

# 3. Para macOS
brew install chromedriver

# 4. Verificar instalação
python check_dependencies.py
```

### Ambiente Docker:

```bash
# 1. Atualizar Dockerfile conforme instruções acima

# 2. Rebuild da imagem
docker-compose build backend

# 3. Reiniciar container
docker-compose up -d backend
```

---

## 🐛 Troubleshooting

### Erro: "ChromeDriver not found"
```bash
# Solução 1: Instalar webdriver-manager
pip install webdriver-manager

# Solução 2: Instalar manualmente
# Ubuntu/Debian:
sudo apt-get install chromium-driver

# macOS:
brew install chromedriver
```

### Erro: "Chrome binary not found"
```bash
# Ubuntu/Debian:
sudo apt-get install chromium-browser

# macOS:
brew install google-chrome
```

### Erro: "DevToolsActivePort file doesn't exist"
Adicione estas opções ao Chrome:
```python
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

### Erro de memória compartilhada no Docker
Adicione ao docker-compose.yml:
```yaml
shm_size: '2gb'
```

---

## 📚 Referências

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- [Webdriver Manager](https://github.com/SergeyPirogov/webdriver_manager)

---

## 💡 Dicas de Performance

1. **Use HTTP quando possível**: Tente primeiro com requisições HTTP simples antes de usar Selenium
2. **Cache de ChromeDriver**: Use webdriver-manager para gerenciar versões automaticamente
3. **Headless Mode**: Sempre use `--headless` em produção
4. **Pool de Drivers**: Para múltiplas consultas paralelas, considere um pool de drivers
5. **Rate Limiting**: Implemente delays entre requisições para evitar bloqueios

---

**Status**: 📦 Dependências documentadas e prontas para instalação
