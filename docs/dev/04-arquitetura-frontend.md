# 4. Arquitetura Frontend - AgroADB

## ⚛️ Visão Geral

O frontend do AgroADB é uma **Single Page Application (SPA)** construída com **React 18** e **TypeScript**, seguindo princípios de **componentes reutilizáveis** e **design system**.

---

## 📁 Estrutura de Pastas

```
frontend/src/
├── components/              # Componentes React
│   ├── ui/                 # UI Kit (40+ componentes)
│   │   ├── Controls.tsx    # Button, Input, Badge, etc
│   │   ├── Cards.tsx       # Cards variados
│   │   ├── Navigation.tsx  # TopNav, Sidebar
│   │   ├── Overlays.tsx    # Modal, Drawer, Tabs
│   │   ├── DataTable.tsx   # Tabela avançada
│   │   └── Form.tsx        # Form controls
│   │
│   └── [outros componentes específicos]
│
├── pages/                   # Páginas da aplicação
│   ├── Dashboard.tsx       # Dashboard principal
│   ├── Investigations.tsx  # Lista de investigações
│   ├── Login.tsx           # Página de login
│   └── ...
│
├── contexts/                # React Contexts
│   ├── AuthContext.tsx     # Estado de autenticação
│   ├── ThemeContext.tsx    # Dark/Light mode
│   └── WebSocketContext.tsx # WebSocket real-time
│
├── lib/                     # Utilitários
│   ├── design-system.ts    # Design tokens
│   ├── api.ts              # Cliente API (Axios)
│   ├── utils.ts            # Funções auxiliares
│   └── hooks.ts            # Custom hooks
│
├── types/                   # Tipos TypeScript
│   ├── investigation.ts
│   ├── user.ts
│   └── ...
│
├── index.css               # Estilos globais
└── main.tsx                # Entry point
```

---

## 🎨 Design System

### Cores

```typescript
const colors = {
  primary: {
    500: '#22c55e',   // Verde principal
    600: '#16a34a',
  },
  secondary: {
    500: '#3b82f6',   // Azul
  },
  // 50+ variações
}
```

### Componentes

```typescript
import { Button, Card, Badge } from '@/components/ui/Controls';

<Button variant="gradient" size="lg">
  Nova Investigação
</Button>

<Card variant="glass" hover>
  Conteúdo
</Card>

<Badge color="success">Ativo</Badge>
```

---

## 🔄 Gerenciamento de Estado

### Context API

```typescript
// AuthContext.tsx
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>(null!);

export const useAuth = () => useContext(AuthContext);
```

### Uso

```typescript
function MyComponent() {
  const { user, logout } = useAuth();
  
  return (
    <div>
      <p>Olá, {user?.full_name}</p>
      <button onClick={logout}>Sair</button>
    </div>
  );
}
```

---

## 🌐 Comunicação com API

### Cliente API

```typescript
// lib/api.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Uso

```typescript
// Criar investigação
const response = await api.post('/investigations', {
  name: 'Fazenda São João',
  type: 'property',
});

// Listar investigações
const { data } = await api.get('/investigations');
```

---

## 🔌 WebSocket

### Conexão

```typescript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Notificação:', data);
};
```

### Context

```typescript
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  return context;
};
```

---

## 🎯 Rotas

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';

<BrowserRouter>
  <Routes>
    <Route path="/" element={<Landing />} />
    <Route path="/login" element={<Login />} />
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/investigations" element={<Investigations />} />
    <Route path="/investigations/:id" element={<InvestigationDetails />} />
  </Routes>
</BrowserRouter>
```

### Proteção de Rotas

```typescript
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return <>{children}</>;
}
```

---

## 🎨 Estilização

### Tailwind CSS

```tsx
<div className="flex items-center gap-4 p-6 rounded-xl bg-white dark:bg-gray-900 shadow-lg hover:shadow-2xl transition-all duration-300">
  <span className="text-lg font-bold text-gray-900 dark:text-white">
    Hello World
  </span>
</div>
```

### Utility Classes Customizadas

```css
.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
}

.gradient-primary {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}
```

---

## 🎭 Animações

### Framer Motion

```tsx
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Conteúdo animado
</motion.div>
```

---

## 🧪 Testes

Ver [docs/dev/06-testes.md](./06-testes.md#frontend)

---

## 📦 Build de Produção

```bash
npm run build
```

Gera:
- `dist/` - Assets otimizados
- Code splitting automático
- Tree shaking
- Minificação
- Source maps

---

**Próximo**: [Banco de Dados](./05-banco-dados.md)
