// API service for health and model information.
import { HealthResponse, ModelInfo } from '../types/api'

const API_URL = import.meta.env.VITE_API_URL || window.location.origin

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/health`)
  if (!response.ok) throw new Error('Failed to fetch health')
  return response.json()
}

export async function getModelInfo(): Promise<ModelInfo> {
  const response = await fetch(`${API_URL}/api/model/info`)
  if (!response.ok) throw new Error('Failed to fetch model info')
  return response.json()
}

export async function getLabels(): Promise<{ labels: string[]; count: number }> {
  const response = await fetch(`${API_URL}/api/labels`)
  if (!response.ok) throw new Error('Failed to fetch labels')
  return response.json()
}
