# 🎨 Integração Frontend - Adicionar Botão OCR

## Como Adicionar o Modal OCR no InvestigationDetailPage

### Passo 1: Importar o Componente

No arquivo `frontend/src/pages/InvestigationDetailPage.tsx`, adicione:

```tsx
// No topo do arquivo, junto com outros imports
import OCRModal from '@/components/OCRModal'
```

### Passo 2: Adicionar Estado

```tsx
// Junto com outros estados (por volta da linha 50)
const [showOCRModal, setShowOCRModal] = useState(false)
```

### Passo 3: Adicionar Botão no Header

Localize a seção de botões de ação (geralmente no `InvestigationHeader`) e adicione:

```tsx
<button
  onClick={() => setShowOCRModal(true)}
  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
>
  <FileText className="w-4 h-4" />
  OCR de Documentos
</button>
```

**Nota:** Importe o ícone `FileText` de `lucide-react`:
```tsx
import { FileText } from 'lucide-react'
```

### Passo 4: Adicionar o Modal

No final do JSX do componente, antes do fechamento final:

```tsx
{/* OCR Modal */}
<OCRModal
  isOpen={showOCRModal}
  onClose={() => setShowOCRModal(false)}
  investigationId={investigation?.id}
  onSuccess={(result) => {
    // Callback quando OCR for bem-sucedido
    console.log('OCR concluído:', result)
    
    // Opcional: Adicionar lógica para processar resultado
    // Por exemplo, extrair CPF/CNPJ e fazer consultas automáticas
    if (result.entities.cpf?.length > 0) {
      // Fazer algo com CPFs encontrados
    }
    if (result.entities.cnpj?.length > 0) {
      // Fazer algo com CNPJs encontrados
    }
  }}
/>
```

### Exemplo Completo de Integração

```tsx
// InvestigationDetailPage.tsx

import { useState } from 'react'
import { FileText } from 'lucide-react'
import OCRModal from '@/components/OCRModal'

export default function InvestigationDetailPage() {
  // ... outros estados
  const [showOCRModal, setShowOCRModal] = useState(false)
  
  // ... resto do componente
  
  return (
    <div>
      {/* Header com botões */}
      <div className="flex gap-2 mb-4">
        {/* Outros botões */}
        
        <button
          onClick={() => setShowOCRModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          title="Extrair texto e entidades de documentos"
        >
          <FileText className="w-4 h-4" />
          OCR
        </button>
      </div>
      
      {/* Resto do conteúdo */}
      
      {/* OCR Modal */}
      <OCRModal
        isOpen={showOCRModal}
        onClose={() => setShowOCRModal(false)}
        investigationId={investigation?.id}
        onSuccess={(result) => {
          console.log('OCR Result:', result)
          
          // Processar entidades encontradas
          const cpfs = result.entities.cpf || []
          const cnpjs = result.entities.cnpj || []
          
          if (cpfs.length > 0 || cnpjs.length > 0) {
            // Mostrar notificação
            alert(`Encontrados: ${cpfs.length} CPF(s) e ${cnpjs.length} CNPJ(s)`)
            
            // Opcional: Adicionar à investigação automaticamente
            // addSubjectsToInvestigation(cpfs, cnpjs)
          }
        }}
      />
    </div>
  )
}
```

---

## Integração Avançada: Processamento Automático

### Processar Entidades Automaticamente

```tsx
const handleOCRSuccess = async (result: OCRResult) => {
  // Extrair entidades
  const cpfs = result.entities.cpf || []
  const cnpjs = result.entities.cnpj || []
  const cars = result.entities.car || []
  
  // Fazer consultas automáticas
  for (const cpf of cpfs) {
    try {
      // Consultar embargos IBAMA
      const embargosResponse = await api.post('/api/v1/integrations/ibama/embargos', {
        cpf_cnpj: cpf,
        investigation_id: investigation.id
      })
      
      if (embargosResponse.data.total > 0) {
        // Mostrar alerta
        showNotification({
          type: 'warning',
          title: 'Embargo Encontrado',
          message: `CPF ${cpf} possui ${embargosResponse.data.total} embargo(s) no IBAMA`
        })
      }
    } catch (error) {
      console.error('Erro ao consultar IBAMA:', error)
    }
  }
  
  // Similar para CNPJs, CARs, etc.
}

// No modal
<OCRModal
  isOpen={showOCRModal}
  onClose={() => setShowOCRModal(false)}
  investigationId={investigation?.id}
  onSuccess={handleOCRSuccess}
/>
```

---

## Adicionar Card de Integrações Ambientais

### Novo Card no Dashboard

```tsx
// InvestigationDetailPage.tsx

const [environmentalData, setEnvironmentalData] = useState({
  embargos: [],
  terrasIndigenas: [],
  unidadesConservacao: []
})

// Função para carregar dados ambientais
const loadEnvironmentalData = async () => {
  if (!investigation) return
  
  try {
    // Buscar embargos para todos CPF/CNPJs da investigação
    const cpfCnpjs = [
      investigation.subject_cpf_cnpj,
      ...investigation.related_subjects?.map(s => s.cpf_cnpj) || []
    ].filter(Boolean)
    
    const embargosPromises = cpfCnpjs.map(doc =>
      api.post('/api/v1/integrations/ibama/embargos', { cpf_cnpj: doc })
    )
    
    const embargosResponses = await Promise.all(embargosPromises)
    const allEmbargos = embargosResponses.flatMap(r => r.data.embargos || [])
    
    setEnvironmentalData(prev => ({
      ...prev,
      embargos: allEmbargos
    }))
  } catch (error) {
    console.error('Erro ao carregar dados ambientais:', error)
  }
}

// Carregar ao montar componente
useEffect(() => {
  loadEnvironmentalData()
}, [investigation?.id])

// Renderizar card
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
    <AlertTriangle className="w-5 h-5 text-orange-600" />
    Questões Ambientais
  </h3>
  
  {environmentalData.embargos.length > 0 ? (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-red-600">
        <AlertTriangle className="w-4 h-4" />
        <span className="font-medium">
          {environmentalData.embargos.length} Embargo(s) IBAMA Encontrado(s)
        </span>
      </div>
      
      {environmentalData.embargos.slice(0, 3).map((embargo, idx) => (
        <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded">
          <p className="font-medium">{embargo.tipo_infracao}</p>
          <p className="text-sm text-gray-600">
            Multa: R$ {embargo.valor_multa.toLocaleString('pt-BR')}
          </p>
          <p className="text-sm text-gray-600">
            {embargo.municipio}/{embargo.uf}
          </p>
        </div>
      ))}
      
      {environmentalData.embargos.length > 3 && (
        <p className="text-sm text-gray-500">
          + {environmentalData.embargos.length - 3} embargo(s) adicional(is)
        </p>
      )}
    </div>
  ) : (
    <p className="text-green-600 flex items-center gap-2">
      <CheckCircle className="w-4 h-4" />
      Nenhum embargo ambiental encontrado
    </p>
  )}
</div>
```

---

## Card de Verificação de Sobreposições

```tsx
// Componente para verificar sobreposições geográficas
const [coordinates, setCoordinates] = useState<{lat: number, lon: number} | null>(null)
const [overlaps, setOverlaps] = useState({
  funai: false,
  icmbio: false,
  terrasIndigenas: [],
  unidadesConservacao: []
})

const checkOverlaps = async (lat: number, lon: number) => {
  try {
    // Verificar FUNAI
    const funaiResponse = await api.post(
      '/api/v1/integrations/funai/verificar-sobreposicao',
      { latitude: lat, longitude: lon, raio_km: 10 }
    )
    
    // Verificar ICMBio
    const icmbioResponse = await api.post(
      '/api/v1/integrations/icmbio/verificar-sobreposicao',
      { latitude: lat, longitude: lon, raio_km: 10 }
    )
    
    setOverlaps({
      funai: funaiResponse.data.tem_sobreposicao,
      icmbio: icmbioResponse.data.tem_sobreposicao,
      terrasIndigenas: funaiResponse.data.terras_sobrepostas || [],
      unidadesConservacao: icmbioResponse.data.unidades_sobrepostas || []
    })
  } catch (error) {
    console.error('Erro ao verificar sobreposições:', error)
  }
}

// Card de sobreposições
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-lg font-bold mb-4">Verificação Geográfica</h3>
  
  {/* Input de coordenadas */}
  <div className="flex gap-2 mb-4">
    <input
      type="number"
      placeholder="Latitude"
      step="0.0001"
      className="flex-1 px-3 py-2 border rounded"
    />
    <input
      type="number"
      placeholder="Longitude"
      step="0.0001"
      className="flex-1 px-3 py-2 border rounded"
    />
    <button
      onClick={() => checkOverlaps(lat, lon)}
      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    >
      Verificar
    </button>
  </div>
  
  {/* Resultados */}
  {overlaps.funai && (
    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded mb-2">
      <div className="flex items-center gap-2 text-yellow-800">
        <AlertTriangle className="w-4 h-4" />
        <span className="font-medium">Sobreposição com Terra Indígena</span>
      </div>
      {overlaps.terrasIndigenas.map((terra, idx) => (
        <p key={idx} className="text-sm text-yellow-700 ml-6">
          • {terra.nome} ({terra.etnia})
        </p>
      ))}
    </div>
  )}
  
  {overlaps.icmbio && (
    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
      <div className="flex items-center gap-2 text-yellow-800">
        <AlertTriangle className="w-4 h-4" />
        <span className="font-medium">Sobreposição com UC</span>
      </div>
      {overlaps.unidadesConservacao.map((uc, idx) => (
        <p key={idx} className="text-sm text-yellow-700 ml-6">
          • {uc.nome} ({uc.categoria})
        </p>
      ))}
    </div>
  )}
</div>
```

---

## Estilos Sugeridos

### Cores para Alertas Ambientais

```tsx
// Embargos IBAMA
className="bg-red-50 border-red-200 text-red-800"

// Sobreposição FUNAI
className="bg-yellow-50 border-yellow-200 text-yellow-800"

// Sobreposição ICMBio
className="bg-orange-50 border-orange-200 text-orange-800"

// Tudo OK
className="bg-green-50 border-green-200 text-green-800"
```

---

## Ícones Sugeridos (lucide-react)

```tsx
import {
  FileText,        // OCR
  AlertTriangle,   // Alertas
  MapPin,          // Localização/Coordenadas
  Shield,          // Proteção Ambiental
  Trees,           // FUNAI/ICMBio
  CheckCircle,     // OK
  XCircle,         // Problema
  Info,            // Informação
} from 'lucide-react'
```

---

## Notificações Toast

```tsx
import { toast } from 'react-hot-toast'

// Sucesso
toast.success('OCR concluído com sucesso!')

// Alerta
toast.warning('Embargo ambiental encontrado!')

// Erro
toast.error('Erro ao processar documento')

// Custom
toast((t) => (
  <div className="flex items-center gap-2">
    <AlertTriangle className="w-5 h-5 text-yellow-600" />
    <div>
      <p className="font-medium">Atenção!</p>
      <p className="text-sm">Sobreposição com área protegida detectada</p>
    </div>
  </div>
))
```

---

## Conclusão

Com essas integrações, o frontend estará completamente conectado às funcionalidades de OCR e consultas ambientais, proporcionando uma experiência rica para o usuário.

Para mais detalhes técnicos, consulte:
- `OCR_INTEGRACOES_AMBIENTAIS.md` - Documentação técnica
- `GUIA_OCR_INTEGRACOES.md` - Guia de uso das APIs
