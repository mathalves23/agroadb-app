import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Edit3, Trash2, Lock, Users, ThumbsUp, CheckCheck } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Comment {
  id: number;
  user_id: number;
  user_name: string;
  content: string;
  is_internal: boolean;
  is_edited: boolean;
  parent_id?: number;
  created_at: string;
  updated_at: string;
}

interface CommentThreadProps {
  investigationId: number;
  currentUserId: number;
}

export default function CommentThread({ investigationId, currentUserId }: CommentThreadProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    loadComments();
  }, [investigationId]);

  const loadComments = async () => {
    try {
      const response = await fetch(
        `/api/v1/collaboration/investigations/${investigationId}/comments`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setComments(data.comments);
      }
    } catch (error) {
      // silenced for production
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(
        `/api/v1/collaboration/investigations/${investigationId}/comments`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            content: newComment,
            is_internal: isInternal
          })
        }
      );

      if (response.ok) {
        setNewComment('');
        setIsInternal(false);
        loadComments();
      }
    } catch (error) {
      // silenced for production
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateComment = async (commentId: number) => {
    try {
      const response = await fetch(
        `/api/v1/collaboration/comments/${commentId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({ content: editContent })
        }
      );

      if (response.ok) {
        setEditingId(null);
        setEditContent('');
        loadComments();
      }
    } catch (error) {
      // silenced for production
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Tem certeza que deseja deletar este comentário?')) return;

    try {
      const response = await fetch(
        `/api/v1/collaboration/comments/${commentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        loadComments();
      }
    } catch (error) {
      // silenced for production
    }
  };

  const getInitials = (name: string) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
  };

  const getAvatarColor = (userId: number) => {
    const colors = [
      'from-indigo-500 to-indigo-700',
      'from-purple-500 to-purple-700',
      'from-pink-500 to-pink-700',
      'from-blue-500 to-blue-700',
      'from-cyan-500 to-cyan-700',
      'from-teal-500 to-teal-700',
    ];
    return colors[userId % colors.length];
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-6">
        <MessageSquare className="h-5 w-5 text-indigo-600" />
        Comentários e Anotações
        <span className="text-sm font-normal text-gray-500">({comments.length})</span>
      </h3>

      {/* New Comment Form */}
      <div className="mb-6 bg-gray-50 rounded-lg p-4">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Adicione um comentário ou anotação... (suporta Markdown)"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none bg-white"
          rows={4}
        />
        
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                type="checkbox"
                checked={isInternal}
                onChange={(e) => setIsInternal(e.target.checked)}
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
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
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>

      {/* Comments List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm font-medium">Nenhum comentário ainda</p>
            <p className="text-xs text-gray-400 mt-1">
              Seja o primeiro a adicionar um comentário ou anotação
            </p>
          </div>
        ) : (
          comments.map((comment) => {
            const isOwn = comment.user_id === currentUserId;
            const avatarColor = getAvatarColor(comment.user_id);
            
            return (
              <div
                key={comment.id}
                className={`flex gap-3 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {/* Avatar */}
                <div className="shrink-0">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${avatarColor} flex items-center justify-center shadow-sm`}>
                    <span className="text-sm font-bold text-white">
                      {getInitials(comment.user_name)}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className={`flex-1 min-w-0 max-w-[80%] ${isOwn ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`p-4 rounded-2xl ${
                      comment.is_internal
                        ? 'bg-amber-50 border border-amber-200'
                        : isOwn
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className={`flex-1 ${isOwn ? 'text-right' : 'text-left'}`}>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-sm font-semibold ${isOwn && !comment.is_internal ? 'text-white' : 'text-gray-900'}`}>
                            {isOwn ? 'Você' : comment.user_name}
                          </span>
                          {comment.is_internal && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
                              <Lock className="h-3 w-3" />
                              Privado
                            </span>
                          )}
                          {comment.is_edited && (
                            <span className={`text-xs ${isOwn && !comment.is_internal ? 'text-indigo-200' : 'text-gray-500'}`}>
                              (editado)
                            </span>
                          )}
                        </div>
                        <span className={`text-xs ${isOwn && !comment.is_internal ? 'text-indigo-200' : 'text-gray-500'}`}>
                          {formatDistanceToNow(new Date(comment.created_at), {
                            addSuffix: true,
                            locale: ptBR
                          })}
                        </span>
                      </div>

                      {/* Actions (owner only) */}
                      {isOwn && editingId !== comment.id && (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => {
                              setEditingId(comment.id);
                              setEditContent(comment.content);
                            }}
                            className={`p-1 rounded transition ${
                              comment.is_internal
                                ? 'text-amber-600 hover:bg-amber-100'
                                : isOwn
                                ? 'text-indigo-200 hover:bg-indigo-500'
                                : 'text-gray-400 hover:bg-gray-200'
                            }`}
                            title="Editar"
                          >
                            <Edit3 className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteComment(comment.id)}
                            className={`p-1 rounded transition ${
                              comment.is_internal
                                ? 'text-amber-600 hover:bg-amber-100'
                                : isOwn
                                ? 'text-indigo-200 hover:bg-indigo-500'
                                : 'text-gray-400 hover:bg-gray-200'
                            }`}
                            title="Deletar"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Comment Text or Edit Form */}
                    {editingId === comment.id ? (
                      <div>
                        <textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                          rows={3}
                        />
                        <div className="flex gap-2 mt-2">
                          <button
                            onClick={() => handleUpdateComment(comment.id)}
                            className="px-3 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded hover:bg-indigo-700 flex items-center gap-1"
                          >
                            <CheckCheck className="h-3 w-3" />
                            Salvar
                          </button>
                          <button
                            onClick={() => {
                              setEditingId(null);
                              setEditContent('');
                            }}
                            className="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-medium rounded hover:bg-gray-300"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className={`text-sm prose prose-sm max-w-none ${isOwn && !comment.is_internal ? 'prose-invert' : ''}`}>
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            a: ({ href, children }) => (
                              <a
                                href={href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className={isOwn && !comment.is_internal ? 'text-indigo-200 hover:text-white underline' : 'text-indigo-600 hover:text-indigo-800 underline'}
                              >
                                {children}
                              </a>
                            ),
                            strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                            em: ({ children }) => <em className="italic">{children}</em>,
                          }}
                        >
                          {comment.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
