import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/chat': 'http://127.0.0.1:8001',
      '/stream_chat': 'http://127.0.0.1:8001',
      '/self_consistency': 'http://127.0.0.1:8001',
      '/modes': 'http://127.0.0.1:8001',
      '/reset': 'http://127.0.0.1:8001',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
