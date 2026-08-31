"""Main App component."""
import { useEffect, useState } from 'react'
import { Header } from './components/Header'
import { CameraPanel } from './components/CameraPanel'
import { PredictionCard } from './components/PredictionCard'
import { TranslationPanel } from './components/TranslationPanel'
import { StatusBadge } from './components/StatusBadge'
import { useCamera } from './hooks/useCamera'
import { usePrediction } from './hooks/usePrediction'
import { getHealth } from './services/api'
import './App.css'

function App() {
  const { isActive } = useCamera()
  const { prediction, wsStatus, sendFrame, connect, disconnect } = usePrediction()
  const [modelLoaded, setModelLoaded] = useState(false)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await getHealth()
        setModelLoaded(health.model_loaded)
      } catch (error) {
        console.error('Health check failed:', error)
      }
    }

    checkHealth()

    // Connect to WebSocket if camera is active
    if (isActive && wsStatus === 'disconnected') {
      connect()
    }

    // Disconnect if camera is stopped
    if (!isActive && wsStatus === 'connected') {
      disconnect()
    }
  }, [isActive, wsStatus, connect, disconnect])

  const handleFrameCapture = (frameBase64: string) => {
    if (wsStatus === 'connected') {
      sendFrame(frameBase64)
    }
  }

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        <div className="container">
          <StatusBadge wsStatus={wsStatus} />

          <div className="layout">
            <div className="panel-left">
              <CameraPanel onFrameCapture={handleFrameCapture} isCapturing={isActive} />
            </div>

            <div className="panel-right">
              <PredictionCard prediction={prediction} modelLoaded={modelLoaded} />
            </div>
          </div>

          <TranslationPanel prediction={prediction} />
        </div>
      </main>

      <footer className="footer">
        <p>
          SignSpeak AI v1.0.0 | Real-Time ISL Recognition |{' '}
          <a href="#privacy">Privacy Policy</a>
        </p>
      </footer>
    </div>
  )
}

export default App
