"""Prediction Card component."""
import { PredictionEvent } from '../types/api'
import './PredictionCard.css'

interface PredictionCardProps {
  prediction: PredictionEvent | null
  modelLoaded: boolean
}

export function PredictionCard({ prediction, modelLoaded }: PredictionCardProps) {
  if (!modelLoaded) {
    return (
      <div className="prediction-card">
        <div className="card-section">
          <h3>Status</h3>
          <p className="status-error">Model Not Loaded</p>
          <p className="status-hint">Inference is unavailable</p>
        </div>
      </div>
    )
  }

  let statusText = 'Waiting...'
  let statusClass = 'status-waiting'
  let signDisplay = '-'
  let confidenceDisplay = '-'

  if (!prediction) {
    statusText = 'No prediction'
  } else if (prediction.type === 'no_hand') {
    statusText = 'No hand detected'
    statusClass = 'status-warning'
  } else if (prediction.type === 'low_confidence') {
    statusText = 'Low confidence'
    statusClass = 'status-warning'
    confidenceDisplay = `${(prediction.confidence! * 100).toFixed(0)}%`
  } else if (prediction.type === 'error') {
    statusText = prediction.message || 'Error'
    statusClass = 'status-error'
  } else if (prediction.type === 'prediction') {
    signDisplay = prediction.sign || '-'
    confidenceDisplay = `${(prediction.confidence! * 100).toFixed(0)}%`

    if (prediction.stable) {
      statusText = 'Stable'
      statusClass = 'status-stable'
    } else {
      statusText = 'Processing...'
      statusClass = 'status-processing'
    }
  }

  return (
    <div className="prediction-card">
      <div className="card-section">
        <h3>Detected Sign</h3>
        <div className="sign-display">{signDisplay}</div>
      </div>

      <div className="card-section">
        <h3>Confidence</h3>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{
              width: `${Math.min(parseFloat(confidenceDisplay) || 0, 100)}%`,
            }}
          />
        </div>
        <p className="confidence-value">{confidenceDisplay}</p>
      </div>

      <div className="card-section">
        <h3>Status</h3>
        <p className={`status-text ${statusClass}`}>{statusText}</p>
        {prediction?.hands_detected !== undefined && (
          <p className="hands-info">Hands: {prediction.hands_detected}</p>
        )}
      </div>
    </div>
  )
}
