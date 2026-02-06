import React, { useState, useEffect } from 'react';
import { X, Share2, UserPlus, Mail, Check, Trash2, Shield, Eye, Edit3, Crown, Search, AlertCircle, MessageCircle } from 'lucide-react';

interface ShareModalProps {
  investigationId: number;
  investigationName: string;
  isOpen: boolean;
  onClose: () => void;
}

interface SharedUser {
  id: number;
  shared_with_id: number;
  shared_with_email: string;
  shared_with_name: string;
  permission: 'view' | 'comment' | 'edit' | 'admin';
  created_at: string;
}

export default function ShareModal({ investigationId, investigationName, isOpen, onClose }: ShareModalProps) {
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState<'view' | 'comment' | 'edit' | 'admin'>('view');
  const [sharedUsers, setSharedUsers] = useState<SharedUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadSharedUsers();
    }
  }, [isOpen, investigationId]);

  const loadSharedUsers = async () => {
    try {
      const response = await fetch(`/api/v1/collaboration/investigations/${investigationId}/shares`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setSharedUsers(data.shares || []);
      }
    } catch (error) {
      // silenced for production
    }
  };

  const handleShare = async () => {
    if (!email.trim()) {
      setError('Digite um email válido');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`/api/v1/collaboration/investigations/${investigationId}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ email, permission })
      });

      if (response.ok) {
        setSuccess('Investigação compartilhada com sucesso!');
        setEmail('');
        setPermission('view');
        loadSharedUsers();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const data = await response.json();
        setError(data.detail || 'Erro ao compartilhar');
      }
    } catch (error) {
      setError('Erro ao compartilhar investigação');
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = async (sharedWithId: number) => {
    if (!confirm('Tem certeza que deseja revogar o acesso?')) return;

    try {
      const response = await fetch(`/api/v1/collaboration/investigations/${investigationId}/shares/${sharedWithId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        setSuccess('Acesso removido com sucesso');
        loadSharedUsers();
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (error) {
      setError('Erro ao revogar acesso');
    }
  };

  const getPermissionIcon = (perm: string) => {
    switch (perm) {
      case 'view': return Eye;
      case 'comment': return MessageCircle;
      case 'edit': return Edit3;
      case 'admin': return Crown;
      default: return Eye;
    }
  };

  const getPermissionLabel = (perm: string) => {
    switch (perm) {
      case 'view': return 'Visualizar';
      case 'comment': return 'Comentar';
      case 'edit': return 'Editar';
      case 'admin': return 'Admin';
      default: return perm;
    }
  };

  const getPermissionColor = (perm: string) => {
    switch (perm) {
      case 'view': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'comment': return 'bg-cyan-100 text-cyan-700 border-cyan-200';
      case 'edit': return 'bg-green-100 text-green-700 border-green-200';
      case 'admin': return 'bg-purple-100 text-purple-700 border-purple-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getInitials = (name: string) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  const getAvatarColor = (name: string) => {
    const colors = [
      'from-indigo-500 to-indigo-700',
      'from-purple-500 to-purple-700',
      'from-pink-500 to-pink-700',
      'from-blue-500 to-blue-700',
      'from-cyan-500 to-cyan-700',
      'from-teal-500 to-teal-700',
      'from-green-500 to-green-700',
      'from-amber-500 to-amber-700',
    ];
    const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[index];
  };

  const filteredUsers = sharedUsers.filter((user) =>
    user.shared_with_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.shared_with_email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Share2 className="h-5 w-5 text-indigo-600" />
              Compartilhar Investigação
            </h2>
            <p className="text-sm text-gray-600 mt-1">{investigationName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Success/Error Messages */}
          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600" />
              <p className="text-sm text-green-800">{success}</p>
            </div>
          )}

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
              <X className="h-4 w-4 text-red-600" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Share Form */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Adicionar Pessoa
            </label>
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleShare()}
                  placeholder="Digite o email do usuário"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <select
                value={permission}
                onChange={(e) => setPermission(e.target.value as any)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="view">Visualizar</option>
                <option value="comment">Comentar</option>
                <option value="edit">Editar</option>
                <option value="admin">Admin</option>
              </select>
              <button
                onClick={handleShare}
                disabled={loading || !email.trim()}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <UserPlus className="h-4 w-4" />
                Compartilhar
              </button>
            </div>

            {/* Permission Info */}
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs font-medium text-gray-700 mb-2">Permissões:</p>
              <ul className="space-y-1 text-xs text-gray-600">
                <li className="flex items-center gap-2">
                  <Eye className="h-3 w-3" />
                  <strong>Visualizar:</strong> Pode ver dados da investigação
                </li>
                <li className="flex items-center gap-2">
                  <MessageCircle className="h-3 w-3" />
                  <strong>Comentar:</strong> Pode visualizar e adicionar comentários
                </li>
                <li className="flex items-center gap-2">
                  <Edit3 className="h-3 w-3" />
                  <strong>Editar:</strong> Pode modificar e adicionar dados
                </li>
                <li className="flex items-center gap-2">
                  <Crown className="h-3 w-3" />
                  <strong>Admin:</strong> Controle total (incluindo compartilhar)
                </li>
              </ul>
            </div>
          </div>

          {/* Shared Users List */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Pessoas com Acesso ({sharedUsers.length})
            </h3>

            {/* Search Bar */}
            {sharedUsers.length > 0 && (
              <div className="mb-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Buscar pessoas..."
                    className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
              </div>
            )}

            {sharedUsers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Share2 className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">Nenhum compartilhamento ainda</p>
                <p className="text-xs text-gray-400 mt-1">
                  Adicione pessoas usando o formulário acima
                </p>
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">Nenhuma pessoa encontrada</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredUsers.map((user) => {
                  const PermIcon = getPermissionIcon(user.permission);
                  const avatarColor = getAvatarColor(user.shared_with_name);
                  
                  return (
                    <div
                      key={user.id}
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition group"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${avatarColor} flex items-center justify-center shadow-sm`}>
                          <span className="text-sm font-bold text-white">
                            {getInitials(user.shared_with_name)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{user.shared_with_name}</p>
                          <p className="text-xs text-gray-600 truncate">{user.shared_with_email}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${getPermissionColor(user.permission)}`}>
                          <PermIcon className="h-3 w-3" />
                          {getPermissionLabel(user.permission)}
                        </span>
                        <button
                          onClick={() => handleRevoke(user.shared_with_id)}
                          className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition opacity-0 group-hover:opacity-100"
                          title="Revogar acesso"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
