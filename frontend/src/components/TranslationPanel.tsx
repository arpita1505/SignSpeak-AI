// Translation Panel component.
import { useEffect, useState } from 'react'
import { PredictionEvent } from '../types/api'
import { speechService } from '../utils/speech'
import './TranslationPanel.css'

interface TranslationPanelProps {
  prediction: PredictionEvent | null
}

export function TranslationPanel({ prediction }: TranslationPanelProps) {
  const [translation, setTranslation] = useState('')
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(true)

  useEffect(() => {
    setSpeechSupported(speechService.isSupported())
  }, [])

  useEffect(() => {
    if (prediction?.type === 'prediction' && prediction.commit && prediction.sign) {
      setTranslation((prev) => prev + prediction.sign)
    }
  }, [prediction])

  const handleSpace = () => {
    setTranslation((prev) => prev + ' ')
  }

  const handleDelete = () => {
    setTranslation((prev) => prev.slice(0, -1))
  }

  const handleClear = () => {
    setTranslation('')
  }

  const handleSpeak = async () => {
    if (!translation.trim() || !speechSupported) return

    try {
      setIsSpeaking(true)
      await speechService.speak(translation)
    } catch (error) {
      console.error('Speech error:', error)
    } finally {
      setIsSpeaking(false)
    }
  }

  const handleSave = async () => {
    if (!translation.trim()) return

    try {
      const response = await fetch('/api/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: translation }),
      })

      if (response.ok) {
        alert('Translation saved!')
      }
    } catch (error) {
      console.error('Save error:', error)
    }
  }

  return (
    <div className="translation-panel">
      <h2>Translation</h2>

      <div className="translation-text">
        <p>{translation || 'Recognition text will appear here...'}</p>
      </div>

      <div className="translation-controls">
        <button className="btn btn-secondary" onClick={handleSpace}>
          Space
        </button>
        <button className="btn btn-secondary" onClick={handleDelete}>
          ← Delete
        </button>
        <button className="btn btn-secondary" onClick={handleClear}>
          Clear
        </button>

        <button
          className="btn btn-primary"
          onClick={handleSpeak}
          disabled={!translation.trim() || !speechSupported || isSpeaking}
        >
          {isSpeaking ? 'Speaking...' : '🔊 Speak'}
        </button>

        <button className="btn btn-primary" onClick={handleSave} disabled={!translation.trim()}>
          💾 Save
        </button>
      </div>

      {!speechSupported && (
        <div className="warning-message">
          ⚠️ Text-to-speech not supported in your browser
        </div>
      )}
    </div>
  )
}
