import { Buffer } from 'buffer'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { TonConnectUIProvider } from '@tonconnect/ui-react'
import App from './App.jsx'
import './index.css'

// @ton/core (used to build the deposit comment cell) needs a global Buffer.
if (typeof window !== 'undefined' && !window.Buffer) {
  window.Buffer = Buffer
}

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <TonConnectUIProvider manifestUrl={manifestUrl}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </TonConnectUIProvider>
  </React.StrictMode>,
)
