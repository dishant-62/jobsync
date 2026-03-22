export interface Job {
  id: string
  company_id: string
  title: string
  location: string
  description: string
  apply_url: string
  posted_date: string
  created_at: string
}

export interface JobListResponse {
  jobs: Job[]
  total: number
}
