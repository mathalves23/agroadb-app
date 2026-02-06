# 🔍 OCR e Integrações Ambientais - Guia Rápido

## 📦 Instalação Rápida

### 1. Instalar Tesseract OCR

```bash
# Execute o script de instalação automática
./install-tesseract.sh
```

Ou instale manualmente:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

### 2. Instalar Dependências Python

```bash
pip install -r backend/requirements.txt
```

### 3. Verificar Instalação

```bash
# Testar OCR
python test_ocr_integrations.py
```

## 🚀 Uso Rápido

### OCR - Extrair Texto de Documentos

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/ocr/process \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@documento.pdf"
```

**Resposta:**
```json
{
  "text": "Texto extraído...",
  "confidence": 0.95,
  "entities": {
    "cpf": ["123.456.789-00"],
    "cnpj": ["12.345.678/0001-90"],
    "car": ["SP-1234567-..."]
  },
  "page_count": 3,
  "processing_time": 2.45
}
```

### IBAMA - Consultar Embargos

```bash
curl -X POST http://localhost:8000/api/v1/integrations/ibama/embargos \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cpf_cnpj": "12.345.678/0001-90"}'
```

### FUNAI - Verificar Sobreposição com Terras Indígenas

```bash
curl -X POST http://localhost:8000/api/v1/integrations/funai/verificar-sobreposicao \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -15.7942,
    "longitude": -47.8822,
    "raio_km": 10.0
  }'
```

**⚠️ Se houver sobreposição:**
```json
{
  "success": true,
  "tem_sobreposicao": true,
  "alerta": "⚠️ SOBREPOSIÇÃO COM TERRA INDÍGENA DETECTADA!",
  "terras_sobrepostas": [
    {
      "nome": "Terra Indígena Xingu",
      "etnia": "Kayapó",
      "fase": "HOMOLOGADA",
      "area_hectares": 2800000.0
    }
  ]
}
```

### ICMBio - Consultar Unidades de Conservação

```bash
curl -X POST http://localhost:8000/api/v1/integrations/icmbio/unidades-conservacao \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"uf": "MT", "grupo": "Proteção Integral"}'
```

## 📚 Endpoints Disponíveis

### OCR
- `POST /api/v1/ocr/process` - Processar documento (PDF/imagem)
- `POST /api/v1/ocr/extract-entities` - Extrair CPF/CNPJ de texto
- `POST /api/v1/ocr/extract-from-image` - Extrair apenas texto de imagem
- `GET /api/v1/ocr/health` - Status do serviço OCR

### IBAMA
- `POST /api/v1/integrations/ibama/embargos` - Consultar embargos ambientais
- `POST /api/v1/integrations/ibama/ctf` - Consultar CTF
- `POST /api/v1/integrations/ibama/auto-infracao` - Consultar auto de infração

### FUNAI
- `POST /api/v1/integrations/funai/terras-indigenas` - Listar terras indígenas
- `POST /api/v1/integrations/funai/verificar-sobreposicao` - Verificar sobreposição

### ICMBio
- `POST /api/v1/integrations/icmbio/unidades-conservacao` - Listar UCs
- `POST /api/v1/integrations/icmbio/verificar-sobreposicao` - Verificar sobreposição

## 🎯 Casos de Uso

### 1. Due Diligence Ambiental Completa

```python
import requests

# 1. Processar documentos com OCR
docs = ['escritura.pdf', 'car.pdf', 'licenca.pdf']
for doc in docs:
    with open(doc, 'rb') as f:
        result = requests.post(
            f'{API_URL}/ocr/process',
            files={'file': f},
            headers={'Authorization': f'Bearer {token}'}
        ).json()
        
        # Extrair CPF/CNPJ dos documentos
        cpf_cnpj = result['entities'].get('cpf', []) + result['entities'].get('cnpj', [])

# 2. Verificar embargos no IBAMA
for doc in cpf_cnpj:
    embargos = requests.post(
        f'{API_URL}/integrations/ibama/embargos',
        json={'cpf_cnpj': doc},
        headers={'Authorization': f'Bearer {token}'}
    ).json()
    
    if embargos['total'] > 0:
        print(f"⚠️ {doc} possui {embargos['total']} embargo(s)")

# 3. Verificar sobreposição com áreas protegidas
coords = (-15.7942, -47.8822)  # Coordenadas da propriedade
funai = requests.post(
    f'{API_URL}/integrations/funai/verificar-sobreposicao',
    json={'latitude': coords[0], 'longitude': coords[1]},
    headers={'Authorization': f'Bearer {token}'}
).json()

icmbio = requests.post(
    f'{API_URL}/integrations/icmbio/verificar-sobreposicao',
    json={'latitude': coords[0], 'longitude': coords[1]},
    headers={'Authorization': f'Bearer {token}'}
).json()

if funai['tem_sobreposicao']:
    print("⚠️ Propriedade sobrepõe terra indígena!")
    
if icmbio['tem_sobreposicao']:
    print("⚠️ Propriedade sobrepõe unidade de conservação!")
```

### 2. Processamento em Lote de Documentos

```python
import os
import glob

# Processar todos PDFs de uma pasta
pdf_folder = './documentos'
resultados = []

for pdf_file in glob.glob(f'{pdf_folder}/*.pdf'):
    print(f"Processando: {pdf_file}")
    
    with open(pdf_file, 'rb') as f:
        result = requests.post(
            f'{API_URL}/ocr/process',
            files={'file': f},
            headers={'Authorization': f'Bearer {token}'}
        ).json()
        
        resultados.append({
            'arquivo': pdf_file,
            'texto': result['text'],
            'entidades': result['entities'],
            'confianca': result['confidence']
        })

# Salvar resultados
import json
with open('resultados_ocr.json', 'w') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)
```

### 3. Monitoramento Automatizado

```python
# Script para rodar diariamente (cron/scheduler)
import schedule
import time

def verificar_novos_embargos():
    """Verifica se novos embargos foram adicionados"""
    
    cpf_cnpj_monitorados = [
        "12.345.678/0001-90",
        "98.765.432/0001-10",
        # ...
    ]
    
    for doc in cpf_cnpj_monitorados:
        embargos = requests.post(
            f'{API_URL}/integrations/ibama/embargos',
            json={'cpf_cnpj': doc},
            headers={'Authorization': f'Bearer {token}'}
        ).json()
        
        if embargos['total'] > 0:
            # Enviar alerta
            enviar_notificacao(
                f"⚠️ ALERTA: {doc} possui {embargos['total']} embargo(s) no IBAMA!"
            )

# Executar diariamente às 9h
schedule.every().day.at("09:00").do(verificar_novos_embargos)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

## 🔧 Troubleshooting

### Erro: "pytesseract not found"

```bash
# Verificar se Tesseract está instalado
tesseract --version

# Se não estiver, instalar
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Erro: "TesseractNotFoundError"

```bash
# Verificar PATH do Tesseract
which tesseract

# Configurar no código (se necessário)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
```

### OCR retornando texto confuso

- Use imagens com boa resolução (mínimo 300 DPI)
- Certifique-se que o documento está bem iluminado
- Evite imagens com muito ruído ou distorções
- Para PDFs escaneados, use qualidade alta no scanner

### APIs IBAMA/FUNAI/ICMBio não retornam dados

- Verifique se os serviços estão disponíveis (podem ter instabilidade)
- Algumas APIs governamentais têm rate limiting
- Estrutura HTML pode mudar (IBAMA usa web scraping)
- WFS pode estar temporariamente indisponível

## 📖 Documentação Completa

Consulte `OCR_INTEGRACOES_AMBIENTAIS.md` para documentação detalhada incluindo:
- Estrutura completa de dados
- Exemplos de código
- Notas técnicas
- Próximos passos

## 🧪 Testes

Execute o script de testes para verificar todas funcionalidades:

```bash
python test_ocr_integrations.py
```

## 📝 Notas Importantes

1. **OCR requer Tesseract instalado no sistema**
2. **IBAMA usa web scraping - pode quebrar se site mudar**
3. **FUNAI/ICMBio dependem de WFS disponível**
4. **Verificações espaciais são aproximadas (usa bbox)**
5. **Todas consultas são auditadas se investigation_id fornecido**

## 🤝 Contribuindo

Para melhorias:
1. Adicione testes para novos casos
2. Documente mudanças em OCR_INTEGRACOES_AMBIENTAIS.md
3. Mantenha compatibilidade com APIs existentes

## 📄 Licença

Mesmo da aplicação principal AgroADB.
