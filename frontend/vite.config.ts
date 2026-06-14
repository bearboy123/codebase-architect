import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Bind to all interfaces (required for Docker/Kubernetes)
    port: 3000,
    proxy: {
      '/api': {
        // In K8s, VITE_API_URL is set to the backend service URL.
        // Falls back to localhost for local development.
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
