import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css';
import App from './App.tsx'
import {QueryClientProvider} from "@tanstack/react-query";
import queryClient from "./lib/query-client.ts";

if (import.meta.env.PROD) {
  createRoot(document.getElementById('root')!).render(
    <QueryClientProvider client={queryClient}>
      <App/>
    </QueryClientProvider>
  )
} else {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App/>
      </QueryClientProvider>
    </StrictMode>
  )
}
