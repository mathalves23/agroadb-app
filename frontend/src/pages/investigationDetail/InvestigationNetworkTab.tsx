import { NetworkGraph } from '@/components/investigation'
import { extractNetworkGraph } from '@/pages/investigationDetail/analysis'

type Props = {
  isLoadingNetwork: boolean
  networkAnalysis: unknown
}

export function InvestigationNetworkTab({ isLoadingNetwork, networkAnalysis }: Props) {
  if (isLoadingNetwork) {
    return (
      <div className="rounded-xl border border-gray-100 bg-white p-12 text-center text-gray-500">
        A carregar grafo de rede…
      </div>
    )
  }

  const graph = extractNetworkGraph(networkAnalysis)
  return <NetworkGraph nodes={graph.nodes} edges={graph.edges} metadata={graph.metadata} />
}
