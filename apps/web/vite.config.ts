import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import process from 'node:process';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/v1': { target: process.env.SIXTH_API_URL || 'http://127.0.0.1:8000', changeOrigin: true },
      '/health': { target: process.env.SIXTH_API_URL || 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
});
