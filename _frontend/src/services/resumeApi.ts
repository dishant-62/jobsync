import type {
  Resume,
  ResumeListResponse,
  ResumeContent,
} from '../types/resume'

const AUTH_BASE = (import.meta.env.VITE_AUTH_URL as string) || 'http://localhost:4000'

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${AUTH_BASE}${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Request failed')
  return data as T
}

export const resumeApi = {
  list: () => apiFetch<ResumeListResponse>('/resume'),

  get: (id: string) => apiFetch<{ resume: Resume }>(`/resume/${id}`),

  create: (payload: { title: string; target_job_title?: string; content?: Partial<ResumeContent> }) =>
    apiFetch<{ resume: Resume }>('/resume', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  update: (
    id: string,
    payload: { title?: string; target_job_title?: string; content?: Partial<ResumeContent> }
  ) =>
    apiFetch<{ resume: Resume }>(`/resume/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  remove: (id: string) => apiFetch<{ message: string }>(`/resume/${id}`, { method: 'DELETE' }),

  setPrimary: (id: string) =>
    apiFetch<{ message: string }>(`/resume/${id}/primary`, { method: 'POST' }),

  analyze: (id: string) =>
    apiFetch<{ resume: Resume }>(`/resume/${id}/analyze`, { method: 'POST' }),
}
