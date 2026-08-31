"""React hook for WebSocket predictions."""
import { useEffect, useState } from 'react'
import { PredictionEvent } from '../types/api'
import { wsService } from '../services/websocket'

export function usePrediction() {
  const [prediction, setPrediction] = useState<PredictionEvent | null>(null)
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>(
    'disconnected'
  )
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const unsubscribeMessage = wsService.onMessage((event) => {
      setPrediction(event)
      if (event.type === 'error') {
        setError(event.message || 'Unknown error')
      }
    })

    const unsubscribeStateChange = wsService.onStateChange((state) => {
      setWsStatus(state)
      if (state === 'disconnected') {
        setError('Disconnected from server')
      } else if (state === 'connected') {
        setError(null)
      }
    })

    return () => {
      unsubscribeMessage()
      unsubscribeStateChange()
    }
  }, [])

  const sendFrame = (frameBase64: string) => {
    wsService.sendFrame(frameBase64)
  }

  const connect = async () => {
    try {
      setError(null)
      await wsService.connect()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const disconnect = () => {
    wsService.disconnect()
  }

  return {
    prediction,
    wsStatus,
    error,
    sendFrame,
    connect,
    disconnect,
  }
}
