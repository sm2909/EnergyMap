import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
        proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        // Add this line to remove '/api' from the URL before sending it to FastAPI
        rewrite: (path) => path.replace(/^\/api/, ''), 
      },
    },
  },
});
