import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { TranslationPanel } from './TranslationPanel'

describe('TranslationPanel', () => {
  it('commits only prediction events explicitly marked for commit', () => {
    const { rerender } = render(<TranslationPanel prediction={null} />)
    rerender(<TranslationPanel prediction={{ type: 'prediction', sign: 'A', confidence: 0.9, stable: true, commit: true }} />)
    expect(screen.getByText('A')).toBeDefined()
    rerender(<TranslationPanel prediction={{ type: 'prediction', sign: 'A', confidence: 0.9, stable: true, commit: false }} />)
    expect(screen.getByText('A')).toBeDefined()
  })

  it('supports space, delete and clear sentence controls', () => {
    render(<TranslationPanel prediction={{ type: 'prediction', sign: 'H', confidence: 0.9, stable: true, commit: true }} />)
    fireEvent.click(screen.getByRole('button', { name: 'Space' }))
    fireEvent.click(screen.getByRole('button', { name: /Delete/ }))
    expect(screen.getByText('H')).toBeDefined()
    fireEvent.click(screen.getByRole('button', { name: 'Clear' }))
    expect(screen.getByText(/Recognition text/)).toBeDefined()
  })

  it('disables speech and save for empty translation', () => {
    render(<TranslationPanel prediction={null} />)
    expect((screen.getByRole('button', { name: /Speak/ }) as HTMLButtonElement).disabled).toBe(true)
    expect((screen.getByRole('button', { name: /Save/ }) as HTMLButtonElement).disabled).toBe(true)
  })
})
