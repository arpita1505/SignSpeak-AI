"""Camera Panel component."""
import { useEffect } from 'react'
import { useCamera } from '../hooks/useCamera'
import './CameraPanel.css'

interface CameraPanelProps {
  onFrameCapture: (frameBase64: string) => void
  isCapturing: boolean
}

export function CameraPanel({ onFrameCapture, isCapturing }: CameraPanelProps) {
  const { videoRef, canvasRef, isActive, error, permission, startCamera, stopCamera, captureFrame } =
    useCamera()

  useEffect(() => {
    if (isCapturing && isActive) {
      const interval = setInterval(() => {
        const frame = captureFrame()
        if (frame) {
          onFrameCapture(frame)
        }
      }, 100) // 10 FPS

      return () => clearInterval(interval)
    }
  }, [isCapturing, isActive, captureFrame, onFrameCapture])

  const handleStart = async () => {
    await startCamera()
  }

  const handleStop = () => {
    stopCamera()
  }

  return (
    <div className="camera-panel">
      <div className="camera-container">
        {permission === 'denied' && (
          <div className="error-message">
            <p>Camera permission denied. Please enable camera access to continue.</p>
          </div>
        )}

        {permission !== 'denied' && !isActive && (
          <div className="placeholder">
            <p>📹 Camera Inactive</p>
            <p>Click "Start Camera" to begin</p>
          </div>
        )}

        {isActive && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="video-element"
            onLoadedMetadata={() => {
              if (videoRef.current) {
                const width = videoRef.current.videoWidth
                const height = videoRef.current.videoHeight
                console.log(`Camera resolution: ${width}x${height}`)
              }
            }}
          />
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      <div className="camera-controls">
        {!isActive ? (
          <button className="btn btn-primary" onClick={handleStart}>
            ▶ Start Camera
          </button>
        ) : (
          <button className="btn btn-danger" onClick={handleStop}>
            ⏹ Stop Camera
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
    </div>
  )
}
