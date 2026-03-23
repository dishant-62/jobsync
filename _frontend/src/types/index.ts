export interface Company {
  id: string
  name: string
}

export interface Job {
  id: string
  company_id: string
  company: Company
  title: string
  location: string
  description: string
  apply_url: string
  posted_date: string
  created_at: string
  skills?: string[] | null
  experience_level?: string | null
  salary_min?: number | null
  salary_max?: number | null
  is_remote: boolean
}

export interface JobListResponse {
  jobs: Job[]
  total: number
}
