import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      // All /api calls proxied through Vite → no browser CORS issues
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Fallback proxy → Render cloud (used when local DB is offline)
      '/render': {
        target: 'https://sanjeeeveni.onrender.com',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/render/, ''),
      }
    }
  }
})
