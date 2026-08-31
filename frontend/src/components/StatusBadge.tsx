"""Status Badge component."""
import { useEffect, useState } from 'react'
import { getHealth } from '../services/api'
import './StatusBadge.css'

interface StatusBadgeProps {
  wsStatus: 'connecting' | 'connected' | 'disconnected'
}

export function StatusBadge({ wsStatus }: StatusBadgeProps) {
  const [modelLoaded, setModelLoaded] = useState(false)
  const [modelVersion, setModelVersion] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await getHealth()
        setModelLoaded(health.model_loaded)
        setModelVersion(health.model_version || null)
      } catch (error) {
        console.error('Health check failed:', error)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000) // Check every 5 seconds

    return () => clearInterval(interval)
  }, [])

  const wsStatusLabel = {
    connecting: 'Connecting...',
    connected: 'Connected',
    disconnected: 'Disconnected',
  }

  return (
    <div className="status-badge-container">
      <div className={`status-badge status-${wsStatus}`}>
        <span className="status-dot" />
        {wsStatusLabel[wsStatus]}
      </div>

      <div className={`status-badge ${modelLoaded ? 'status-ready' : 'status-error'}`}>
        <span className="status-dot" />
        Model: {modelLoaded ? 'Ready' : 'Not Loaded'}
      </div>

      {modelVersion && (
        <div className="status-badge status-info">
          v{modelVersion}
        </div>
      )}
    </div>
  )
}
