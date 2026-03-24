import axios from 'axios'
import type { JobListResponse } from '../types'

// Use /api/v1 proxy in development, or direct URL in production
const API_BASE_URL = import.meta.env.DEV ? '/api/v1' : import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export interface SearchFilters {
  q?: string
  location?: string
  experience_level?: string
  is_remote?: boolean
  skills?: string[]
  limit?: number
  offset?: number
}

export const jobApi = {
  /**
   * Fetch all jobs with optional search, filters, and pagination
   */
  listJobs: async (filters: SearchFilters = {}): Promise<JobListResponse> => {
    const { limit = 20, offset = 0, ...filterParams } = filters
    
    const params: any = {
      limit,
      offset,
    }

    if (filterParams.q) params.q = filterParams.q
    if (filterParams.location) params.location = filterParams.location
    if (filterParams.experience_level) params.experience_level = filterParams.experience_level
    if (filterParams.is_remote !== undefined && filterParams.is_remote === true) {
      params.is_remote = true
    }
    // Note: Skills filtering will be implemented when backend JSON array filtering is ready
    // if (filterParams.skills && filterParams.skills.length > 0) {
    //   params.skills = filterParams.skills.join(',')
    // }

    const response = await client.get<JobListResponse>('/jobs', { params })
    return response.data
  },

  /**
   * Fetch a single job by ID
   */
  getJob: async (jobId: string) => {
    const response = await client.get(`/jobs/${jobId}`)
    return response.data
  },

  /**
   * Save a job for the current user
   */
  saveJob: async (jobId: string) => {
    const response = await client.post(`/jobs/${jobId}/save`)
    return response.data
  },

  /**
   * Remove a saved job for the current user
   */
  unsaveJob: async (jobId: string) => {
    await client.delete(`/jobs/${jobId}/save`)
  },

  /**
   * Check if a job is saved by the current user
   */
  isJobSaved: async (jobId: string): Promise<boolean> => {
    try {
      await client.get(`/jobs/${jobId}/save`)
      return true
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      throw error
    }
  },

  /**
   * Get all saved jobs for the current user
   */
  getSavedJobs: async (): Promise<JobListResponse> => {
    const response = await client.get('/saved-jobs')
    return { jobs: response.data, total: response.data.length }
  },
}
