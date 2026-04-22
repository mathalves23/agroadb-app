import { useCallback, useEffect, useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { CheckCheck, CloudOff, Edit3, Lock, MessageSquare, Send, Trash2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { isSafeHttpUrl } from '@/lib/safeUrl'
import {
  collaborationService,
  type InvestigationComment,
} from '@/services/collaborationService'

type LocalComment = InvestigationComment & {
  pendingSync?: boolean
}

interface CommentThreadProps {
  investigationId: number
  currentUserId: number
  currentUserName?: string
}

export default function CommentThread({
  investigationId,
  currentUserId,
  currentUserName = 'Você',
}: CommentThreadProps) {
  const [comments, setComments] = useState<LocalComment[]>([])
  const [newComment, setNewComment] = useState('')
  const [isInternal, setIsInternal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')

  const loadComments = useCallback(async () => {
    try {
      const data = await collaborationService.listComments(investigationId)
      setComments(data)
    } catch {
      // silenced for production
    }
  }, [investigationId])

  useEffect(() => {
    void loadComments()
  }, [loadComments])

  const handleAddComment = async () => {
    if (!newComment.trim()) return

    setLoading(true)
    try {
      const content = newComment
      const result = await collaborationService.addComment(investigationId, {
        content,
        is_internal: isInternal,
      })

      if (result.queued) {
        setComments((prev) => [
          {
            id: -Date.now(),
            user_id: currentUserId,
            user_name: currentUserName,
            content,
            is_internal: isInternal,
            is_edited: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            pendingSync: true,
          },
          ...prev,
        ])
      } else {
        await loadComments()
      }
    } catch {
      // silenced for production
    } finally {
      setNewComment('')
      setIsInternal(false)
      setLoading(false)
    }
  }

  const handleUpdateComment = async (commentId: number) => {
    try {
      const result = await collaborationService.updateComment(commentId, editContent)
      if (result.queued) {
        setComments((prev) =>
          prev.map((comment) =>
            comment.id === commentId
              ? {
                  ...comment,
                  content: editContent,
                  is_edited: true,
                  updated_at: new Date().toISOString(),
                  pendingSync: true,
                }
              : comment
          )
        )
      } else {
        await loadComments()
      }

      setEditingId(null)
      setEditContent('')
    } catch {
      // silenced for production
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Tem certeza que deseja deletar este comentário?')) return

    try {
      const result = await collaborationService.deleteComment(commentId)
      if (result.queued) {
        setComments((prev) => prev.filter((comment) => comment.id !== commentId))
      } else {
        await loadComments()
      }
    } catch {
      // silenced for production
    }
  }

  const getInitials = (name: string) => {
    if (!name) return '?'
    return name
      .split(' ')
      .map((segment) => segment[0])
      .slice(0, 2)
      .join('')
      .toUpperCase()
  }

  const getAvatarColor = (userId: number) => {
    const colors = [
      'from-indigo-500 to-indigo-700',
      'from-purple-500 to-purple-700',
      'from-pink-500 to-pink-700',
      'from-blue-500 to-blue-700',
      'from-cyan-500 to-cyan-700',
      'from-teal-500 to-teal-700',
    ]
    return colors[Math.abs(userId) % colors.length]
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-6 flex items-center gap-2 text-lg font-semibold text-gray-900">
        <MessageSquare className="h-5 w-5 text-indigo-600" />
        Comentários e Anotações
        <span className="text-sm font-normal text-gray-500">({comments.length})</span>
      </h3>

      <div className="mb-6 rounded-lg bg-gray-50 p-4">
        <textarea
          value={newComment}
          onChange={(event) => setNewComment(event.target.value)}
          placeholder="Adicione um comentário ou anotação... (suporta Markdown)"
          className="w-full resize-none rounded-lg border border-gray-300 bg-white px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
          rows={4}
        />

        <div className="mt-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={isInternal}
                onChange={(event) => setIsInternal(event.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <Lock className="h-4 w-4 text-gray-400" />
              <span>Anotação privada</span>
            </label>
            <div className="text-xs text-gray-500">
              <strong>Dica:</strong> Use **negrito**, *itálico*, [links](url)
            </div>
          </div>

          <button
            onClick={handleAddComment}
            disabled={loading || !newComment.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="py-12 text-center text-gray-500">
            <MessageSquare className="mx-auto mb-3 h-12 w-12 text-gray-300" />
            <p className="text-sm font-medium">Nenhum comentário ainda</p>
            <p className="mt-1 text-xs text-gray-400">
              Seja o primeiro a adicionar um comentário ou anotação
            </p>
          </div>
        ) : (
          comments.map((comment) => {
            const isOwn = comment.user_id === currentUserId
            const avatarColor = getAvatarColor(comment.user_id)

            return (
              <div
                key={comment.id}
                className={`flex gap-3 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div className="shrink-0">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br ${avatarColor} shadow-sm`}
                  >
                    <span className="text-sm font-bold text-white">
                      {getInitials(comment.user_name)}
                    </span>
                  </div>
                </div>

                <div
                  className={`min-w-0 max-w-[80%] flex-1 ${isOwn ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`rounded-2xl p-4 ${
                      comment.is_internal
                        ? 'border border-amber-200 bg-amber-50'
                        : isOwn
                        ? 'bg-indigo-600 text-white'
                        : 'border border-gray-200 bg-gray-100'
                    }`}
                  >
                    <div className="mb-2 flex items-start justify-between gap-2">
                      <div className={`flex-1 ${isOwn ? 'text-right' : 'text-left'}`}>
                        <div className="mb-1 flex items-center gap-2">
                          <span
                            className={`text-sm font-semibold ${
                              isOwn && !comment.is_internal ? 'text-white' : 'text-gray-900'
                            }`}
                          >
                            {isOwn ? 'Você' : comment.user_name}
                          </span>
                          {comment.is_internal && (
                            <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                              <Lock className="h-3 w-3" />
                              Privado
                            </span>
                          )}
                          {comment.pendingSync && (
                            <span
                              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                                isOwn && !comment.is_internal
                                  ? 'bg-white/15 text-white'
                                  : 'bg-slate-100 text-slate-600'
                              }`}
                            >
                              <CloudOff className="h-3 w-3" />
                              A sincronizar
                            </span>
                          )}
                          {comment.is_edited && (
                            <span
                              className={`text-xs ${
                                isOwn && !comment.is_internal ? 'text-indigo-200' : 'text-gray-500'
                              }`}
                            >
                              (editado)
                            </span>
                          )}
                        </div>
                        <span
                          className={`text-xs ${
                            isOwn && !comment.is_internal ? 'text-indigo-200' : 'text-gray-500'
                          }`}
                        >
                          {formatDistanceToNow(new Date(comment.created_at), {
                            addSuffix: true,
                            locale: ptBR,
                          })}
                        </span>
                      </div>

                      {isOwn && editingId !== comment.id && (
                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            onClick={() => {
                              setEditingId(comment.id)
                              setEditContent(comment.content)
                            }}
                            className={`rounded-lg p-1.5 transition ${
                              comment.is_internal
                                ? 'text-amber-700 hover:bg-amber-100'
                                : 'text-white/70 hover:bg-white/10 hover:text-white'
                            }`}
                            title="Editar"
                          >
                            <Edit3 className="h-3.5 w-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDeleteComment(comment.id)}
                            className={`rounded-lg p-1.5 transition ${
                              comment.is_internal
                                ? 'text-amber-700 hover:bg-amber-100'
                                : 'text-white/70 hover:bg-white/10 hover:text-white'
                            }`}
                            title="Deletar"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      )}
                    </div>

                    {editingId === comment.id ? (
                      <div className="space-y-3">
                        <textarea
                          value={editContent}
                          onChange={(event) => setEditContent(event.target.value)}
                          className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
                          rows={3}
                        />
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setEditingId(null)
                              setEditContent('')
                            }}
                            className="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100"
                          >
                            Cancelar
                          </button>
                          <button
                            type="button"
                            onClick={() => handleUpdateComment(comment.id)}
                            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-indigo-700"
                          >
                            <CheckCheck className="h-3.5 w-3.5" />
                            Guardar
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div
                        className={`prose prose-sm max-w-none text-sm ${
                          isOwn && !comment.is_internal ? 'prose-invert' : ''
                        }`}
                      >
                        <ReactMarkdown
                          components={{
                            a: ({ href, children, ...props }) => {
                              const safeHref = href && isSafeHttpUrl(href) ? href : undefined
                              return (
                                <a
                                  {...props}
                                  href={safeHref}
                                  target="_blank"
                                  rel="noreferrer noopener"
                                  className={
                                    isOwn && !comment.is_internal
                                      ? 'text-white underline'
                                      : 'text-indigo-600 underline'
                                  }
                                >
                                  {children}
                                </a>
                              )
                            },
                          }}
                        >
                          {comment.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
