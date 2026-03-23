/**
 * API Service Layer
 * Provides clean interface for fetching job data from the backend
 */

import type { Job, JobListResponse } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

/**
 * Fetch all jobs with optional search and pagination
 */
export async function fetchJobs(params: {
  q?: string
  location?: string
  limit?: number
  offset?: number
} = {}): Promise<JobListResponse> {
  const queryParams = new URLSearchParams()

  if (params.q) queryParams.append('q', params.q)
  if (params.location) queryParams.append('location', params.location)
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.offset) queryParams.append('offset', params.offset.toString())

  const url = `${BASE_URL}/jobs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch jobs: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Fetch a single job by ID
 */
export async function fetchJobById(id: string): Promise<Job> {
  const url = `${BASE_URL}/jobs/${id}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Job not found')
    }
    throw new Error(`Failed to fetch job: ${response.statusText}`)
  }

  return response.json()
}
