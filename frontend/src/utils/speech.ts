"""Speech synthesis utilities."""

export class SpeechService {
  private synth: SpeechSynthesis
  private utterance: SpeechSynthesisUtterance | null = null

  constructor() {
    this.synth = window.speechSynthesis
  }

  speak(text: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!text.trim()) {
        reject(new Error('Empty text'))
        return
      }

      // Cancel any ongoing speech
      this.synth.cancel()

      this.utterance = new SpeechSynthesisUtterance(text)
      this.utterance.lang = 'en-IN' // Indian English
      this.utterance.rate = 1.0
      this.utterance.pitch = 1.0

      this.utterance.onend = () => resolve()
      this.utterance.onerror = (error) => reject(error)

      this.synth.speak(this.utterance)
    })
  }

  stop(): void {
    this.synth.cancel()
  }

  isSupported(): boolean {
    return 'speechSynthesis' in window
  }

  isSpeaking(): boolean {
    return this.synth.speaking
  }
}

export const speechService = new SpeechService()
