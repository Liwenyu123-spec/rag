import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// GitHub Pages 项目页路径为 /rag/；本地与 FastAPI 托管用 /
const pages = process.env.GITHUB_PAGES === 'true'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: pages ? '/rag/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/chat': 'http://127.0.0.1:8001',
      '/stream_chat': 'http://127.0.0.1:8001',
      '/self_consistency': 'http://127.0.0.1:8001',
      '/product_copy': 'http://127.0.0.1:8001',
      '/social_plan': 'http://127.0.0.1:8001',
      '/social_plan_stream': 'http://127.0.0.1:8001',
      '/compare': 'http://127.0.0.1:8001',
      '/tool_chat': 'http://127.0.0.1:8001',
      '/system_prompt': 'http://127.0.0.1:8001',
      '/health': 'http://127.0.0.1:8001',
      '/modes': 'http://127.0.0.1:8001',
      '/reset': 'http://127.0.0.1:8001',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
