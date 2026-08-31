// React hook for camera management.
import { useEffect, useRef, useState } from 'react'
import { cameraService } from '../utils/camera'

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isActive, setIsActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [permission, setPermission] = useState<'pending' | 'granted' | 'denied'>('pending')

  const startCamera = async () => {
    try {
      setError(null)
      const success = await cameraService.requestAccess()
      if (!success) {
        setPermission('denied')
        setError('Camera permission denied')
        return
      }

      setPermission('granted')
      if (videoRef.current) {
        cameraService.attachToVideo(videoRef.current)
        setIsActive(true)
      }
    } catch (err) {
      setError((err as Error).message)
      setPermission('denied')
    }
  }

  const stopCamera = () => {
    cameraService.stop()
    setIsActive(false)
  }

  const captureFrame = (): string | null => {
    if (!canvasRef.current) return null
    return cameraService.getFrame(canvasRef.current)
  }

  useEffect(() => {
    return () => {
      cameraService.stop()
    }
  }, [])

  return {
    videoRef,
    canvasRef,
    isActive,
    error,
    permission,
    startCamera,
    stopCamera,
    captureFrame,
  }
}
