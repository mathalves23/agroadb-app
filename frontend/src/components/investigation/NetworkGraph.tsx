import { useEffect, useRef, useState } from 'react'
import ForceGraph2D, {
  type ForceGraphMethods,
  type GraphData,
  type LinkObject,
  type NodeObject,
} from 'react-force-graph-2d'
import { Network, TrendingUp, Users, Building } from 'lucide-react'

interface NetworkNode {
  id: string
  label: string
  type: 'company' | 'property' | 'person'
  attributes: Record<string, unknown>
  x?: number
  y?: number
  fx?: number
  fy?: number
}

interface NetworkEdge {
  source: string
  target: string
  type: string
  weight: number
  attributes: Record<string, unknown>
}

type FGNode = NodeObject<NetworkNode>
type FGLinkExtra = { type: string; weight: number; attributes: Record<string, unknown> }
type FGLink = LinkObject<FGNode, FGLinkExtra>

function isFgNode(value: unknown): value is FGNode {
  if (typeof value !== 'object' || value === null) return false
  const o = value as { id?: unknown; label?: unknown; type?: unknown }
  return typeof o.id === 'string' && typeof o.label === 'string' && typeof o.type === 'string'
}

interface NetworkGraphProps {
  nodes: NetworkNode[]
  edges: NetworkEdge[]
  metadata?: {
    num_nodes: number
    num_edges: number
    density: number
    is_connected: boolean
  }
}

export function NetworkGraph({ nodes, edges, metadata }: NetworkGraphProps) {
  const graphRef = useRef<ForceGraphMethods<FGNode, FGLink> | undefined>(undefined)
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null)
  const [highlightNodes, setHighlightNodes] = useState(new Set<string>())
  const [highlightLinks, setHighlightLinks] = useState(new Set<string>())
  const [hoverNode, setHoverNode] = useState<NetworkNode | null>(null)

  // Cores por tipo de nó
  const getNodeColor = (node: NetworkNode) => {
    switch (node.type) {
      case 'company':
        return '#3b82f6' // blue-500
      case 'property':
        return '#10b981' // green-500
      case 'person':
        return '#f59e0b' // amber-500
      default:
        return '#6b7280' // gray-500
    }
  }

  // Ícone por tipo
  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'company':
        return '🏢'
      case 'property':
        return '🏞️'
      case 'person':
        return '👤'
      default:
        return '⚫'
    }
  }

  // Tamanho do nó baseado em conexões
  const getNodeSize = (node: NetworkNode) => {
    const connections = edges.filter(
      (e) => e.source === node.id || e.target === node.id
    ).length
    return Math.max(5, Math.min(15, 5 + connections))
  }

  // Pintar nó customizado
  const paintNode = (node: FGNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label
    const fontSize = 12 / globalScale
    const size = getNodeSize(node)

    // Desenhar círculo
    ctx.beginPath()
    const nx = node.x ?? 0
    const ny = node.y ?? 0
    ctx.arc(nx, ny, size, 0, 2 * Math.PI, false)
    ctx.fillStyle = getNodeColor(node)
    
    // Highlight se selecionado ou hover
    if (highlightNodes.has(String(node.id)) || hoverNode?.id === String(node.id)) {
      ctx.shadowBlur = 10
      ctx.shadowColor = getNodeColor(node)
    } else {
      ctx.shadowBlur = 0
    }
    
    ctx.fill()
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 2
    ctx.stroke()

    // Desenhar ícone
    ctx.font = `${fontSize}px Sans-Serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(getNodeIcon(node.type), nx, ny)

    // Desenhar label
    if (highlightNodes.has(String(node.id)) || hoverNode?.id === String(node.id) || globalScale > 1.5) {
      ctx.font = `${fontSize}px Sans-Serif`
      ctx.fillStyle = '#1f2937'
      ctx.fillText(label, nx, ny + size + fontSize)
    }
  }

  // Pintar aresta customizada
  const paintLink = (link: FGLink, ctx: CanvasRenderingContext2D) => {
    const resolveEndpoint = (p: typeof link.source): FGNode | null => {
      if (p == null) return null
      if (typeof p === 'object' && isFgNode(p)) return p
      return null
    }
    const start = resolveEndpoint(link.source)
    const end = resolveEndpoint(link.target)
    if (!start || !end) return

    // Cor baseada no tipo de relação
    let color = '#d1d5db' // gray-300
    if (link.type === 'owns') color = '#10b981' // green-500
    if (link.type === 'leases') color = '#f59e0b' // amber-500
    if (link.type === 'partner_in') color = '#8b5cf6' // purple-500

    // Espessura baseada no peso
    const width = Math.max(1, Math.min(5, link.weight ?? 1))

    // Highlight
    const pair = `${String(start.id)}-${String(end.id)}`
    if (highlightLinks.has(pair)) {
      ctx.strokeStyle = color
      ctx.lineWidth = width + 1
      ctx.globalAlpha = 1
    } else {
      ctx.strokeStyle = color
      ctx.lineWidth = width
      ctx.globalAlpha = 0.3
    }

    // Desenhar linha
    ctx.beginPath()
    ctx.moveTo(start.x ?? 0, start.y ?? 0)
    ctx.lineTo(end.x ?? 0, end.y ?? 0)
    ctx.stroke()
    ctx.globalAlpha = 1
  }

  // Atualizar highlights quando nó é selecionado
  useEffect(() => {
    if (!selectedNode) {
      setHighlightNodes(new Set())
      setHighlightLinks(new Set())
      return
    }

    const connectedNodes = new Set<string>([selectedNode.id])
    const connectedLinks = new Set<string>()

    edges.forEach((edge) => {
      if (edge.source === selectedNode.id || edge.target === selectedNode.id) {
        connectedLinks.add(`${edge.source}-${edge.target}`)
        connectedNodes.add(edge.source === selectedNode.id ? edge.target : edge.source)
      }
    })

    setHighlightNodes(connectedNodes)
    setHighlightLinks(connectedLinks)
  }, [selectedNode, edges])

  // Criar dados do grafo
  const graphData = {
    nodes: nodes.map((n) => ({ ...n })),
    links: edges.map((e) => ({
      source: e.source,
      target: e.target,
      type: e.type,
      weight: e.weight,
      attributes: e.attributes,
    })),
  } as GraphData<FGNode, FGLink>

  return (
    <div className="space-y-4">
      {/* Estatísticas */}
      {metadata && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2">
              <div className="bg-blue-100 rounded-lg p-2">
                <Network className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Nós</p>
                <p className="text-xl font-semibold text-gray-900">{metadata.num_nodes}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2">
              <div className="bg-green-100 rounded-lg p-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Conexões</p>
                <p className="text-xl font-semibold text-gray-900">{metadata.num_edges}</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2">
              <div className="bg-purple-100 rounded-lg p-2">
                <Users className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Densidade</p>
                <p className="text-xl font-semibold text-gray-900">
                  {(metadata.density * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2">
              <div className={`${metadata.is_connected ? 'bg-green-100' : 'bg-amber-100'} rounded-lg p-2`}>
                <Building className={`h-4 w-4 ${metadata.is_connected ? 'text-green-600' : 'text-amber-600'}`} />
              </div>
              <div>
                <p className="text-xs text-gray-500">Rede</p>
                <p className="text-sm font-semibold text-gray-900">
                  {metadata.is_connected ? 'Conectada' : 'Fragmentada'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legenda */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Legenda</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span className="text-xs text-gray-700">🏢 Empresas</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-xs text-gray-700">🏞️ Propriedades</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500"></div>
            <span className="text-xs text-gray-700">👤 Pessoas</span>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            💡 Clique em um nó para destacar suas conexões. Use o scroll para zoom e arraste para mover.
          </p>
        </div>
      </div>

      {/* Grafo */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={Math.min(window.innerWidth - 100, 1200)}
          height={600}
          nodeCanvasObject={paintNode}
          linkCanvasObject={paintLink}
          onNodeClick={(node) => {
            if (node && isFgNode(node)) setSelectedNode(node as NetworkNode)
          }}
          onNodeHover={(node) => {
            if (node && isFgNode(node)) setHoverNode(node as NetworkNode)
          }}
          enableNodeDrag={true}
          enableZoomInteraction={true}
          enablePanInteraction={true}
          cooldownTime={3000}
          d3VelocityDecay={0.3}
          d3AlphaDecay={0.02}
        />
      </div>

      {/* Detalhes do nó selecionado */}
      {selectedNode && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-lg"
                style={{ backgroundColor: getNodeColor(selectedNode) }}
              >
                {getNodeIcon(selectedNode.type)}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900">{selectedNode.label}</h3>
                <p className="text-xs text-gray-500 capitalize">{selectedNode.type}</p>
              </div>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-gray-600 text-sm"
            >
              ✕
            </button>
          </div>

          {/* Atributos */}
          {Object.keys(selectedNode.attributes).length > 0 && (
            <div className="space-y-2">
              {Object.entries(selectedNode.attributes)
                .filter(([key]) => key !== 'type' && key !== 'label')
                .map(([key, value]) => (
                  <div key={key} className="flex justify-between text-xs">
                    <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                    <span className="text-gray-900 font-medium">
                      {value ? String(value) : '—'}
                    </span>
                  </div>
                ))}
            </div>
          )}

          {/* Conexões */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">
              Conexões ({highlightNodes.size - 1})
            </p>
            <div className="space-y-1">
              {Array.from(highlightNodes)
                .filter((nodeId) => nodeId !== selectedNode.id)
                .slice(0, 5)
                .map((nodeId) => {
                  const node = nodes.find((n) => n.id === nodeId)
                  if (!node) return null
                  return (
                    <div key={nodeId} className="flex items-center gap-2 text-xs">
                      <span>{getNodeIcon(node.type)}</span>
                      <span className="text-gray-700">{node.label}</span>
                    </div>
                  )
                })}
              {highlightNodes.size > 6 && (
                <p className="text-xs text-gray-500">
                  + {highlightNodes.size - 6} outras conexões
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Mensagem se vazio */}
      {nodes.length === 0 && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-12 text-center">
          <Network className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-4 text-base font-medium text-gray-900">
            Nenhuma conexão encontrada
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Adicione empresas e propriedades à investigação para visualizar a rede de relacionamentos.
          </p>
        </div>
      )}
    </div>
  )
}
