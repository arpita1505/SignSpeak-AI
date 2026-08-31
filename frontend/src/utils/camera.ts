// Camera utilities for webcam access and frame capture.

export class CameraService {
  private stream: MediaStream | null = null
  private video: HTMLVideoElement | null = null

  async requestAccess(): Promise<boolean> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      })
      return true
    } catch (error) {
      console.error('Camera access error:', error)
      return false
    }
  }

  attachToVideo(videoElement: HTMLVideoElement): void {
    this.video = videoElement
    if (this.stream) {
      videoElement.srcObject = this.stream
    }
  }

  getFrame(canvas: HTMLCanvasElement): string | null {
    if (!this.video) return null

    try {
      const ctx = canvas.getContext('2d')
      if (!ctx) return null

      canvas.width = this.video.videoWidth
      canvas.height = this.video.videoHeight
      ctx.drawImage(this.video, 0, 0)

      return canvas.toDataURL('image/jpeg', 0.8).split(',')[1] // Return base64
    } catch (error) {
      console.error('Failed to capture frame:', error)
      return null
    }
  }

  stop(): void {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop())
      this.stream = null
    }
    if (this.video) {
      this.video.srcObject = null
    }
  }

  isActive(): boolean {
    return this.stream !== null && this.stream.active
  }
}

export const cameraService = new CameraService()
