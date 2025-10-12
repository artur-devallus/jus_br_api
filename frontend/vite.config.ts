import path from 'path';
import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({command}) => ({
  plugins: [react()],
  // Adiciona a configuração de teste
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts', // Arquivo de configuração para os testes
    css: true,
  },
  build: {
    emptyOutDir: true,
    chunkSizeWarningLimit: 2000
  },
  base: command === 'serve' ? '/' : '/jusbr/',
  // Adiciona path aliases
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
}));