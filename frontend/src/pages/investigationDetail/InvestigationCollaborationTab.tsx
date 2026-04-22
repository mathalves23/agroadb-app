import { History as HistoryIcon, MessageSquare, Share2 } from 'lucide-react'

import ChangeLog from '@/components/ChangeLog'
import CommentThread from '@/components/CommentThread'

type Props = {
  currentUserId: number | null
  currentUserName: string
  investigationId: number
  onShare: () => void
}

export function InvestigationCollaborationTab({
  currentUserId,
  currentUserName,
  investigationId,
  onShare,
}: Props) {
  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="mb-2 text-2xl font-bold">Colaboração e Histórico</h2>
            <p className="text-indigo-100">
              Compartilhe a investigação, adicione comentários e acompanhe todas as alterações
            </p>
          </div>
          <button
            onClick={onShare}
            className="flex items-center gap-2 rounded-lg bg-white px-5 py-3 font-semibold text-indigo-600 shadow-lg transition hover:bg-indigo-50"
          >
            <Share2 className="h-5 w-5" />
            Compartilhar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-100 p-3">
              <Share2 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Compartilhamentos</p>
              <p className="text-2xl font-bold text-gray-900">-</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-cyan-100 p-3">
              <MessageSquare className="h-6 w-6 text-cyan-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Comentários</p>
              <p className="text-2xl font-bold text-gray-900">-</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-indigo-100 p-3">
              <HistoryIcon className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Alterações</p>
              <p className="text-2xl font-bold text-gray-900">-</p>
            </div>
          </div>
        </div>
      </div>

      {currentUserId && (
        <CommentThread
          investigationId={investigationId}
          currentUserId={currentUserId}
          currentUserName={currentUserName}
        />
      )}

      <ChangeLog investigationId={investigationId} />
    </div>
  )
}
