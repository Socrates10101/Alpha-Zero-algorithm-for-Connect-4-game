import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'log-requests',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const timestamp = new Date().toISOString();
          console.log(`[${timestamp}] ${req.method} ${req.url} - ${req.headers['user-agent']}`);
          
          // Log response status
          const originalEnd = res.end;
          res.end = function(...args) {
            console.log(`[${timestamp}] Response: ${res.statusCode} for ${req.url}`);
            originalEnd.apply(res, args);
          };
          
          next();
        });
      }
    }
  ],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    hmr: {
      overlay: true
    },
    watch: {
      usePolling: true
    }
  },
  logLevel: 'info',
  clearScreen: false
})
