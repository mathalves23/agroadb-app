import { useState, useEffect, useCallback } from 'react';
import {
  X,
  Share2,
  UserPlus,
  Mail,
  Check,
  Trash2,
  Shield,
  Eye,
  Edit3,
  Crown,
  Search,
  AlertCircle,
  MessageCircle,
  Link2,
  Copy,
  Clock,
  Download,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { investigationService, type GuestLinkPublic } from '@/services/investigationService';

interface ShareModalProps {
  investigationId: number;
  investigationName: string;
  isOpen: boolean;
  onClose: () => void;
  /** Dono da investigação: criar/listar/revogar links de convidado sem conta. */
  canManageGuestLinks?: boolean;
}

function authHeaders(): HeadersInit {
  const token = useAuthStore.getState().accessToken;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function appBasePrefix(): string {
  const base = (import.meta.env.BASE_URL || '/').replace(/\/+/g, '/');
  if (base === '/' || base === '') return '';
  return base.endsWith('/') ? base.slice(0, -1) : base;
}

function absoluteGuestUrl(guestViewPath: string): string {
  const prefix = appBasePrefix();
  const path = guestViewPath.startsWith('/') ? guestViewPath : `/${guestViewPath}`;
  return `${window.location.origin}${prefix}${path}`;
}

interface SharedUser {
  id: number;
  shared_with_id: number;
  shared_with_email: string;
  shared_with_name: string;
  permission: 'view' | 'comment' | 'edit' | 'admin';
  created_at: string;
}

export default function ShareModal({
  investigationId,
  investigationName,
  isOpen,
  onClose,
  canManageGuestLinks = false,
}: ShareModalProps) {
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState<'view' | 'comment' | 'edit' | 'admin'>('view');
  const [sharedUsers, setSharedUsers] = useState<SharedUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const [guestLinks, setGuestLinks] = useState<GuestLinkPublic[]>([]);
  const [guestLabel, setGuestLabel] = useState('');
  const [guestExpiryPreset, setGuestExpiryPreset] = useState<'none' | '7d' | '30d' | 'custom'>('30d');
  const [guestCustomExpires, setGuestCustomExpires] = useState('');
  const [guestAllowDownloads, setGuestAllowDownloads] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);
  const [guestCreatedUrl, setGuestCreatedUrl] = useState<string | null>(null);
  const [guestCreatedToken, setGuestCreatedToken] = useState<string | null>(null);

  const loadSharedUsers = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/collaboration/investigations/${investigationId}/shares`, {
        headers: {
          ...authHeaders(),
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSharedUsers(data.shares || []);
      }
    } catch (error) {
      // silenced for production
    }
  }, [investigationId]);

  const loadGuestLinks = useCallback(async () => {
    if (!canManageGuestLinks) return;
    try {
      const data = await investigationService.listGuestLinks(investigationId);
      setGuestLinks(data.items || []);
    } catch {
      setGuestLinks([]);
    }
  }, [canManageGuestLinks, investigationId]);

  useEffect(() => {
    if (isOpen) {
      void loadSharedUsers();
      void loadGuestLinks();
    }
  }, [isOpen, loadSharedUsers, loadGuestLinks]);

  useEffect(() => {
    if (!isOpen) {
      setGuestCreatedUrl(null);
      setGuestCreatedToken(null);
      setGuestLabel('');
      setGuestAllowDownloads(false);
      setGuestExpiryPreset('30d');
      setGuestCustomExpires('');
    }
  }, [isOpen]);

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
          ...authHeaders(),
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
          ...authHeaders(),
        },
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

  const computeGuestExpiresIso = (): string | undefined => {
    if (guestExpiryPreset === 'none') return undefined;
    if (guestExpiryPreset === '7d') return new Date(Date.now() + 7 * 864e5).toISOString();
    if (guestExpiryPreset === '30d') return new Date(Date.now() + 30 * 864e5).toISOString();
    if (guestExpiryPreset === 'custom' && guestCustomExpires) {
      const d = new Date(guestCustomExpires);
      if (!Number.isNaN(d.getTime())) return d.toISOString();
    }
    return undefined;
  };

  const handleCreateGuestLink = async () => {
    setGuestLoading(true);
    setError('');
    setSuccess('');
    try {
      const expiresAt = computeGuestExpiresIso();
      const res = await investigationService.createGuestLink(investigationId, {
        label: guestLabel.trim() ? guestLabel.trim() : null,
        expires_at: expiresAt ?? null,
        allow_downloads: guestAllowDownloads,
      });
      setGuestCreatedUrl(absoluteGuestUrl(res.guest_view_path));
      setGuestCreatedToken(res.token);
      setSuccess('Link de convidado criado. Copie o URL agora — o token secreto não volta a ser mostrado.');
      await loadGuestLinks();
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: string } } };
      const detail = ax.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Erro ao criar link de convidado');
    } finally {
      setGuestLoading(false);
    }
  };

  const handleRevokeGuestLink = async (linkId: number) => {
    if (!confirm('Revogar este link? Quem tiver o URL deixará de conseguir aceder.')) return;
    setError('');
    try {
      await investigationService.revokeGuestLink(investigationId, linkId);
      setSuccess('Link revogado.');
      await loadGuestLinks();
    } catch {
      setError('Erro ao revogar link');
    }
  };

  const copyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccess('Copiado para a área de transferência.');
      setTimeout(() => setSuccess(''), 2500);
    } catch {
      setError('Não foi possível copiar para a área de transferência.');
    }
  };

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
                onChange={(e) => {
                  const v = e.target.value
                  if (v === 'view' || v === 'comment' || v === 'edit' || v === 'admin') setPermission(v)
                }}
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

          {canManageGuestLinks && (
            <div className="mb-8 rounded-xl border border-indigo-100 bg-indigo-50/40 p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-1 flex items-center gap-2">
                <Link2 className="h-4 w-4 text-indigo-600" />
                Link para convidado (data room leve)
              </h3>
              <p className="text-xs text-gray-600 mb-4">
                Partilha só de leitura sem conta AgroADB: URL revogável, prazo opcional, registo de
                acessos no servidor. Por defeito não permite exportar PDF; active abaixo se o
                diligente precisar de download.
              </p>

              {guestCreatedUrl && guestCreatedToken && (
                <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 space-y-2">
                  <p className="text-xs font-medium text-amber-900">
                    Guarde este link — o token completo só é mostrado uma vez.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => void copyText(guestCreatedUrl)}
                      className="inline-flex items-center gap-1 rounded-md bg-white px-2 py-1 text-xs font-medium text-amber-900 border border-amber-200 hover:bg-amber-100"
                    >
                      <Copy className="h-3 w-3" />
                      Copiar URL
                    </button>
                    <button
                      type="button"
                      onClick={() => void copyText(guestCreatedToken)}
                      className="inline-flex items-center gap-1 rounded-md bg-white px-2 py-1 text-xs font-medium text-amber-900 border border-amber-200 hover:bg-amber-100"
                    >
                      <Copy className="h-3 w-3" />
                      Copiar token
                    </button>
                  </div>
                  <p className="text-[11px] text-amber-800 break-all font-mono">{guestCreatedUrl}</p>
                </div>
              )}

              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Etiqueta (opcional)</label>
                  <input
                    type="text"
                    value={guestLabel}
                    onChange={(e) => setGuestLabel(e.target.value)}
                    placeholder="Ex.: Cliente — Due diligence Q2"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    Expiração
                  </label>
                  <select
                    value={guestExpiryPreset}
                    onChange={(e) => {
                      const v = e.target.value;
                      if (v === 'none' || v === '7d' || v === '30d' || v === 'custom') setGuestExpiryPreset(v);
                    }}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="none">Sem expiração</option>
                    <option value="7d">7 dias</option>
                    <option value="30d">30 dias</option>
                    <option value="custom">Data e hora…</option>
                  </select>
                </div>
              </div>
              {guestExpiryPreset === 'custom' && (
                <div className="mt-3">
                  <label className="block text-xs font-medium text-gray-700 mb-1">Expira em</label>
                  <input
                    type="datetime-local"
                    value={guestCustomExpires}
                    onChange={(e) => setGuestCustomExpires(e.target.value)}
                    className="w-full max-w-xs px-3 py-2 text-sm border border-gray-300 rounded-lg"
                  />
                </div>
              )}
              <label className="mt-3 flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={guestAllowDownloads}
                  onChange={(e) => setGuestAllowDownloads(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <Download className="h-4 w-4 text-gray-500" />
                Permitir exportação PDF por este link
              </label>
              <button
                type="button"
                onClick={() => void handleCreateGuestLink()}
                disabled={guestLoading}
                className="mt-3 px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {guestLoading ? 'A criar…' : 'Gerar link de convidado'}
              </button>

              <div className="mt-6 border-t border-indigo-100 pt-4">
                <h4 className="text-xs font-semibold text-gray-800 mb-2">Links existentes</h4>
                {guestLinks.length === 0 ? (
                  <p className="text-xs text-gray-500">Ainda não há links criados.</p>
                ) : (
                  <ul className="space-y-2 max-h-48 overflow-y-auto">
                    {guestLinks.map((gl) => {
                      const revoked = Boolean(gl.revoked_at);
                      return (
                        <li
                          key={gl.id}
                          className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs"
                        >
                          <div className="min-w-0">
                            <p className="font-medium text-gray-900 truncate">
                              {gl.label || `Link #${gl.id}`}
                              {revoked && (
                                <span className="ml-2 text-red-600 font-normal">Revogado</span>
                              )}
                            </p>
                            <p className="text-gray-500">
                              Acessos: {gl.access_count}
                              {gl.last_access_at
                                ? ` · Último: ${new Date(gl.last_access_at).toLocaleString()}`
                                : ''}
                              {gl.expires_at ? ` · Expira: ${new Date(gl.expires_at).toLocaleString()}` : ''}
                              {gl.allow_downloads ? ' · PDF permitido' : ' · Só leitura'}
                            </p>
                          </div>
                          {!revoked && (
                            <button
                              type="button"
                              onClick={() => void handleRevokeGuestLink(gl.id)}
                              className="shrink-0 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                              title="Revogar link"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            </div>
          )}

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
