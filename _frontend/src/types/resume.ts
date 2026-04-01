// ── Resume domain types ───────────────────────────────────────────────────────

export interface ResumeContact {
  email: string
  phone: string
  location: string
  linkedin: string
  github: string
  website: string
}

export interface ResumeEducation {
  institution: string
  degree: string
  field: string
  start_date: string
  end_date: string
  gpa: string
  description: string
}

export interface ResumeExperience {
  company: string
  title: string
  location: string
  start_date: string
  end_date: string
  is_current: boolean
  bullets: string[]
}

export interface ResumeProject {
  name: string
  url: string
  description: string
  tech_stack: string[]
}

export interface ResumeContent {
  name: string
  summary: string
  contact: ResumeContact
  education: ResumeEducation[]
  experience: ResumeExperience[]
  projects: ResumeProject[]
  skills: string[]
}

export type SuggestionType = 'urgent' | 'critical' | 'optional'

export interface ResumeSuggestion {
  section: string
  type: SuggestionType
  issue: string
  suggestion: string
  improved_text: string
}

export type ResumeScore = 'A' | 'B' | 'C' | 'D' | 'F' | null
export type AnalysisStatus = 'pending' | 'analyzing' | 'complete' | 'error'

export interface Resume {
  _id: string
  user_id: string
  title: string
  target_job_title: string
  is_primary: boolean
  content: ResumeContent
  score: ResumeScore
  score_label: string | null
  analysis_summary: string | null
  suggestions: ResumeSuggestion[]
  analysis_status: AnalysisStatus
  created_at: string
  updated_at: string
}

/** Lighter version returned by the list endpoint (no suggestions/content) */
export type ResumeListItem = Omit<Resume, 'suggestions' | 'content'>

export interface ResumeListResponse {
  resumes: ResumeListItem[]
  total: number
  slots: number
}
