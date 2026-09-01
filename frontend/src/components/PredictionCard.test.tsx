import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PredictionCard } from './PredictionCard'

describe('PredictionCard', () => {
  it('shows an explicit model unavailable state', () => {
    render(<PredictionCard prediction={null} modelLoaded={false} />)
    expect(screen.getByText('Model Not Loaded')).toBeDefined()
  })

  it('renders sign, confidence, hand count and stability', () => {
    render(<PredictionCard modelLoaded prediction={{ type: 'prediction', sign: 'B', confidence: 0.87, stable: true, commit: true, hands_detected: 2 }} />)
    expect(screen.getByText('B')).toBeDefined()
    expect(screen.getByText('87%')).toBeDefined()
    expect(screen.getByText('Stable')).toBeDefined()
    expect(screen.getByText('Hands: 2')).toBeDefined()
  })
})
