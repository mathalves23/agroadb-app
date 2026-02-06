import { useState } from 'react'
import { Upload, FileText, X, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'
import { api } from '@/services/api'

interface OCRModalProps {
  isOpen: boolean
  onClose: () => void
  investigationId?: number
  onSuccess?: (result: OCRResult) => void
}

interface OCRResult {
  text: string
  confidence: number
  entities: Record<string, string[]>
  page_count: number
  processing_time: number
  metadata: Record<string, any>
}

export default function OCRModal({ isOpen, onClose, investigationId, onSuccess }: OCRModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<OCRResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      handleFileSelect(selectedFile)
    }
  }

  const handleFileSelect = (selectedFile: File) => {
    // Validar tipo
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp']
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Formato não suportado. Use PDF ou imagens (JPG, PNG, TIFF, BMP)')
      return
    }

    // Validar tamanho (50MB)
    const maxSize = 50 * 1024 * 1024
    if (selectedFile.size > maxSize) {
      setError('Arquivo muito grande. Máximo: 50MB')
      return
    }

    setFile(selectedFile)
    setError(null)
    setResult(null)
  }

  const handleProcess = async () => {
    if (!file) return

    setIsProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post<OCRResult>('/api/v1/ocr/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
      if (onSuccess) {
        onSuccess(response.data)
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erro ao processar documento'
      setError(errorMsg)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleClose = () => {
    setFile(null)
    setResult(null)
    setError(null)
    setIsProcessing(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold">OCR - Extrair Texto de Documento</h2>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isProcessing}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Upload Area */}
          {!result && (
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragging
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              
              {!file ? (
                <>
                  <p className="text-lg mb-2">Arraste um arquivo ou clique para selecionar</p>
                  <p className="text-sm text-gray-500 mb-4">
                    PDF, JPG, PNG, TIFF, BMP (até 50MB)
                  </p>
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png,.tiff,.bmp"
                    onChange={handleFileInput}
                    disabled={isProcessing}
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700"
                  >
                    Selecionar Arquivo
                  </label>
                </>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center gap-2">
                    <FileText className="w-6 h-6 text-blue-600" />
                    <span className="font-medium">{file.name}</span>
                    <span className="text-sm text-gray-500">
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                  </div>
                  
                  <div className="flex gap-2 justify-center">
                    <button
                      onClick={handleProcess}
                      disabled={isProcessing}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Processando...
                        </>
                      ) : (
                        'Processar com OCR'
                      )}
                    </button>
                    
                    <button
                      onClick={() => {
                        setFile(null)
                        setError(null)
                      }}
                      disabled={isProcessing}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                    >
                      Trocar Arquivo
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Erro</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="space-y-4">
              {/* Success Banner */}
              <div className="flex items-start gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-green-900">Processamento concluído!</p>
                  <p className="text-sm text-green-700">
                    {result.page_count} página(s) processada(s) em {result.processing_time.toFixed(2)}s
                    • Confiança: {(result.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Entities Found */}
              {Object.keys(result.entities).length > 0 && (
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-3">Entidades Detectadas</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(result.entities).map(([type, values]) => (
                      <div key={type} className="space-y-1">
                        <p className="text-sm font-medium text-gray-700 uppercase">{type}</p>
                        <div className="flex flex-wrap gap-1">
                          {values.map((value, idx) => (
                            <span
                              key={idx}
                              className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                            >
                              {value}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Extracted Text */}
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-3">Texto Extraído</h3>
                <div className="bg-gray-50 rounded p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm whitespace-pre-wrap font-mono">{result.text}</pre>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(result.text)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Copiar Texto
                </button>
                
                <button
                  onClick={() => {
                    setFile(null)
                    setResult(null)
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Processar Outro Documento
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {!result && (
          <div className="p-6 border-t bg-gray-50">
            <p className="text-sm text-gray-600">
              💡 <strong>Dica:</strong> O OCR funciona melhor com imagens nítidas e bem iluminadas.
              PDFs com texto nativo são processados instantaneamente.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
