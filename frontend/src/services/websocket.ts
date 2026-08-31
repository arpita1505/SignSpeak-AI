// WebSocket service for real-time predictions.
import { PredictionEvent } from '../types/api'

export class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private messageHandlers: ((event: PredictionEvent) => void)[] = []
  private stateHandlers: ((state: 'connecting' | 'connected' | 'disconnected') => void)[] = []
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private state: 'connecting' | 'connected' | 'disconnected' = 'disconnected'
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private intentionalClose = false
  private framePending = false

  constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = import.meta.env.VITE_API_URL || window.location.host
    this.url = `${protocol}://${host}/ws/predict`
  }

  connect(): Promise<void> {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) return Promise.resolve()
    this.intentionalClose = false
    return new Promise((resolve, reject) => {
      try {
        this.state = 'connecting'
        this.notifyStateChange('connecting')

        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          this.state = 'connected'
          this.reconnectAttempts = 0
          this.notifyStateChange('connected')
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.framePending = false
          try {
            const message: PredictionEvent = JSON.parse(event.data)
            this.notifyMessage(message)
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          this.state = 'disconnected'
          this.notifyStateChange('disconnected')
          this.ws = null
          this.framePending = false
          if (!this.intentionalClose) this.attemptReconnect()
        }
      } catch (e) {
        this.state = 'disconnected'
        this.notifyStateChange('disconnected')
        reject(e)
      }
    })
  }

  disconnect(): void {
    this.intentionalClose = true
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.reconnectTimer = null
    if (this.ws) {
      this.ws.close()
      this.ws = null
      this.state = 'disconnected'
      this.notifyStateChange('disconnected')
    }
  }

  sendFrame(frameBase64: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN && !this.framePending) {
      try {
        const message = JSON.stringify({ frame: frameBase64 })
        this.ws.send(message)
        this.framePending = true
      } catch (e) {
        console.error('Failed to send frame:', e)
      }
    }
  }

  onMessage(handler: (event: PredictionEvent) => void): () => void {
    this.messageHandlers.push(handler)
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler)
    }
  }

  onStateChange(handler: (state: 'connecting' | 'connected' | 'disconnected') => void): () => void {
    this.stateHandlers.push(handler)
    return () => {
      this.stateHandlers = this.stateHandlers.filter((h) => h !== handler)
    }
  }

  getState(): 'connecting' | 'connected' | 'disconnected' {
    return this.state
  }

  isConnected(): boolean {
    return this.state === 'connected'
  }

  private notifyMessage(event: PredictionEvent): void {
    this.messageHandlers.forEach((handler) => handler(event))
  }

  private notifyStateChange(state: 'connecting' | 'connected' | 'disconnected'): void {
    this.stateHandlers.forEach((handler) => handler(state))
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch((e) => {
        console.error('Reconnection failed:', e)
      })
    }, delay)
  }
}

export const wsService = new WebSocketService()
