import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true, // No cambiar de puerto si está ocupado
    host: '0.0.0.0', // Escuchar en todas las interfaces
  },
})
