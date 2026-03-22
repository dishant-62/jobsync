import axios from 'axios'
import type { JobListResponse } from '../types'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const jobApi = {
  /**
   * Fetch all jobs with optional search and pagination
   */
  listJobs: async (
    q?: string,
    location?: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<JobListResponse> => {
    const response = await client.get<JobListResponse>('/jobs', {
      params: {
        ...(q && { q }),
        ...(location && { location }),
        limit,
        offset,
      },
    })
    return response.data
  },

  /**
   * Fetch a single job by ID
   */
  getJob: async (jobId: string) => {
    const response = await client.get(`/jobs/${jobId}`)
    return response.data
  },
}
