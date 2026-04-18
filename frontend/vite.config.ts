import { defineConfig, splitVendorChunkPlugin } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

/** Base pública (ex.: `/agroadb/` para GitHub Pages). Definir `VITE_BASE_PATH` no build. */
function viteBase(): string {
  const raw = (process.env.VITE_BASE_PATH ?? '/').trim() || '/'
  if (raw === '/') return '/'
  return raw.endsWith('/') ? raw : `${raw}/`
}

export default defineConfig(({ mode }) => ({
  base: viteBase(),
  plugins: [react(), splitVendorChunkPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'es2020',
    sourcemap: mode === 'development',
    cssCodeSplit: true,
    chunkSizeWarningLimit: 600,
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'zustand'],
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    headers: {
      'X-Content-Type-Options': 'nosniff',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
}))
