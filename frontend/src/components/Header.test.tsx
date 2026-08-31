"""Tests for Header component."""
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Header } from '../Header'

describe('Header', () => {
  it('renders title', () => {
    render(<Header />)
    expect(screen.getByText('SignSpeak AI')).toBeDefined()
  })

  it('renders subtitle', () => {
    render(<Header />)
    expect(screen.getByText(/Real-Time Indian Sign Language/)).toBeDefined()
  })
})
