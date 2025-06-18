import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import App from './App.tsx'
import App3D from './App3D.tsx'

// Add logging for debugging
console.log('Main.tsx loaded at:', new Date().toISOString());

// Log when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded at:', new Date().toISOString());
});

// Log any errors
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

const rootElement = document.getElementById('root');
if (rootElement) {
  console.log('Root element found, rendering app...');
  createRoot(rootElement).render(
    <StrictMode>
      <App3D />
    </StrictMode>,
  );
  console.log('App rendered successfully');
} else {
  console.error('Root element not found!');
}
