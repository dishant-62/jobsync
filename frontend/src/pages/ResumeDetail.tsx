import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { resumeApi } from '../services/resumeApi'
import { useAuth } from '../context/AuthContext'
import { AISuggestionsPanel } from '../components/resume/AISuggestionsPanel'
import type { Resume, ResumeContact } from '../types/resume'

/* ─── Grade badge ────────────────────────────────────────── */
const GRADE_STYLES: Record<string, { ring: string; text: string; bg: string }> = {
  A: { ring: 'ring-emerald-400', text: 'text-emerald-600', bg: 'bg-emerald-50' },
  B: { ring: 'ring-blue-400', text: 'text-blue-600', bg: 'bg-blue-50' },
  C: { ring: 'ring-amber-400', text: 'text-amber-500', bg: 'bg-amber-50' },
  D: { ring: 'ring-orange-400', text: 'text-orange-500', bg: 'bg-orange-50' },
  F: { ring: 'ring-red-400', text: 'text-red-600', bg: 'bg-red-50' },
}

function GradeBadge({ grade }: { grade: string }) {
  const s = GRADE_STYLES[grade] ?? GRADE_STYLES['F']
  return (
    <div className={`w-20 h-20 rounded-full ring-4 ${s.ring} ${s.bg} flex items-center justify-center`}>
      <span className={`text-4xl font-black ${s.text}`}>{grade}</span>
    </div>
  )
}

/* ─── Stat pill ──────────────────────────────────────────── */
function Stat({ count, label, color }: { count: number; label: string; color: string }) {
  return (
    <div className="text-center">
      <p className={`text-2xl font-bold ${color}`}>{count}</p>
      <p className="text-xs text-gray-400 mt-0.5">{label}</p>
    </div>
  )
}

/* ─── Section card ───────────────────────────────────────── */
function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-white shadow-sm p-5">
      <h3 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">{title}</h3>
      {children}
    </div>
  )
}

/* ─── Main component ─────────────────────────────────────── */
export default function ResumeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user, isInitialising } = useAuth()

  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [tab, setTab] = useState<'suggestions' | 'content'>('suggestions')

  // Redirect if not logged in
  useEffect(() => {
    if (!isInitialising && !user) navigate('/')
  }, [isInitialising, user, navigate])

  const loadResume = useCallback(async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const { resume: data } = await resumeApi.get(id)
      setResume(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load resume')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (user) loadResume()
  }, [user, loadResume])

  // Poll while analyzing
  useEffect(() => {
    if (resume?.analysis_status !== 'analyzing') return
    const timer = setInterval(async () => {
      try {
        const { resume: fresh } = await resumeApi.get(id!)
        setResume(fresh)
        if (fresh.analysis_status !== 'analyzing') clearInterval(timer)
      } catch {
        clearInterval(timer)
      }
    }, 3000)
    return () => clearInterval(timer)
  }, [resume?.analysis_status, id])

  async function handleAnalyze() {
    if (!id) return
    setAnalyzing(true)
    try {
      const { resume: updated } = await resumeApi.analyze(id)
      setResume(updated)
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  async function handleDelete() {
    if (!id || !window.confirm('Delete this resume? This cannot be undone.')) return
    try {
      await resumeApi.remove(id)
      navigate('/resume')
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  /* ─── Loading / error states ─── */
  if (isInitialising || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-black border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-4">
        <p className="text-gray-600">{error ?? 'Resume not found'}</p>
        <button
          onClick={() => navigate('/resume')}
          className="rounded-full bg-black text-white px-5 py-2 text-sm"
        >
          Back to Resumes
        </button>
      </div>
    )
  }

  const urgent = resume.suggestions.filter((s) => s.type === 'urgent').length
  const critical = resume.suggestions.filter((s) => s.type === 'critical').length
  const optional = resume.suggestions.filter((s) => s.type === 'optional').length
  const isAnalyzing = analyzing || resume.analysis_status === 'analyzing'

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-10">
        {/* Back */}
        <button
          onClick={() => navigate('/resume')}
          className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-700 mb-6 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          All Resumes
        </button>

        {/* Header card */}
        <div className="rounded-2xl bg-white border border-gray-100 shadow-sm p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-center">
            {/* Grade */}
            {resume.score ? (
              <GradeBadge grade={resume.score} />
            ) : (
              <div className="w-20 h-20 rounded-full ring-2 ring-dashed ring-gray-200 bg-gray-50 flex items-center justify-center shrink-0">
                <span className="text-2xl font-black text-gray-300">?</span>
              </div>
            )}

            {/* Title + meta */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-bold text-gray-900 truncate">{resume.title}</h1>
                {resume.is_primary && (
                  <span className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-black text-white">
                    Primary
                  </span>
                )}
              </div>
              {resume.target_job_title && (
                <p className="text-sm text-gray-400 mt-0.5">Target: {resume.target_job_title}</p>
              )}
              {resume.score_label && (
                <p className="text-sm font-medium text-gray-600 mt-1">{resume.score_label}</p>
              )}
              {resume.analysis_summary && (
                <p className="text-sm text-gray-500 mt-2 line-clamp-2">{resume.analysis_summary}</p>
              )}
            </div>

            {/* Stats */}
            {resume.analysis_status === 'complete' && (
              <div className="flex gap-5 shrink-0 border-l border-gray-100 pl-5">
                <Stat count={urgent} label="Urgent" color="text-red-500" />
                <Stat count={critical} label="Critical" color="text-amber-500" />
                <Stat count={optional} label="Optional" color="text-blue-400" />
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2 mt-5">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="flex items-center gap-2 rounded-full bg-black text-white px-5 py-2 text-sm font-medium hover:bg-gray-800 transition-colors disabled:opacity-60"
            >
              {isAnalyzing ? (
                <>
                  <span className="w-3.5 h-3.5 border border-white border-t-transparent rounded-full animate-spin" />
                  Analysing…
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  {resume.analysis_status === 'complete' ? 'Re-Analyse' : 'Analyse Resume'}
                </>
              )}
            </button>

            <button
              onClick={handleDelete}
              className="rounded-full border border-gray-200 text-gray-600 px-5 py-2 text-sm font-medium hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-gray-100 rounded-full p-1 w-fit">
          {(['suggestions', 'content'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-1.5 rounded-full text-sm font-medium transition-colors ${
                tab === t ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t === 'suggestions' ? 'AI Suggestions' : 'Content'}
            </button>
          ))}
        </div>

        {/* Tab panels */}
        {tab === 'suggestions' && (
          <div className="rounded-2xl bg-white border border-gray-100 shadow-sm p-6">
            <AISuggestionsPanel suggestions={resume.suggestions} />
          </div>
        )}

        {tab === 'content' && (
          <div className="space-y-5">
            {resume.content?.summary && (
              <SectionCard title="Summary">
                <p className="text-sm text-gray-700 leading-relaxed">{resume.content.summary}</p>
              </SectionCard>
            )}

            {resume.content?.contact && (
              <SectionCard title="Contact">
                <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
                  {(['email', 'phone', 'location', 'linkedin', 'github', 'website'] as (keyof ResumeContact)[]).map(
                    (key) =>
                      resume.content!.contact?.[key] ? (
                        <div key={key} className="flex gap-2">
                          <dt className="text-gray-400 capitalize">{key}:</dt>
                          <dd className="text-gray-700 truncate">{resume.content!.contact![key]}</dd>
                        </div>
                      ) : null
                  )}
                </dl>
              </SectionCard>
            )}

            {resume.content?.experience?.length ? (
              <SectionCard title="Experience">
                <div className="space-y-4">
                  {resume.content.experience.map((exp, i) => (
                    <div key={i} className="border-l-2 border-gray-100 pl-4">
                      <p className="font-semibold text-sm text-gray-800">
                        {exp.title} · {exp.company}
                      </p>
                      <p className="text-xs text-gray-400">
                        {exp.start_date} – {exp.end_date ?? 'Present'} {exp.location ? `· ${exp.location}` : ''}
                      </p>
                      {exp.bullets?.length ? (
                        <ul className="mt-2 space-y-1 list-disc list-inside text-sm text-gray-600">
                          {exp.bullets.map((b, j) => (
                            <li key={j}>{b}</li>
                          ))}
                        </ul>
                      ) : null}
                    </div>
                  ))}
                </div>
              </SectionCard>
            ) : null}

            {resume.content?.education?.length ? (
              <SectionCard title="Education">
                <div className="space-y-3">
                  {resume.content.education.map((edu, i) => (
                    <div key={i}>
                      <p className="font-semibold text-sm text-gray-800">{edu.degree} in {edu.field}</p>
                      <p className="text-xs text-gray-500">{edu.institution}</p>
                      <p className="text-xs text-gray-400">
                        {edu.start_date} – {edu.end_date ?? 'Present'}
                        {edu.gpa ? ` · GPA ${edu.gpa}` : ''}
                      </p>
                    </div>
                  ))}
                </div>
              </SectionCard>
            ) : null}

            {resume.content?.skills?.length ? (
              <SectionCard title="Skills">
                <div className="flex flex-wrap gap-2">
                  {resume.content.skills.map((skill, i) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-gray-100 text-sm text-gray-700">
                      {skill}
                    </span>
                  ))}
                </div>
              </SectionCard>
            ) : null}

            {resume.content?.projects?.length ? (
              <SectionCard title="Projects">
                <div className="space-y-4">
                  {resume.content.projects.map((proj, i) => (
                    <div key={i}>
                      <p className="font-semibold text-sm text-gray-800">{proj.name}</p>
                      {proj.description && (
                        <p className="text-sm text-gray-600 mt-0.5">{proj.description}</p>
                      )}
                      {proj.tech_stack?.length ? (
                        <div className="flex flex-wrap gap-1.5 mt-1.5">
                          {proj.tech_stack.map((t, j) => (
                            <span key={j} className="px-2 py-0.5 rounded bg-gray-100 text-xs text-gray-500">{t}</span>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </SectionCard>
            ) : null}

            {!resume.content && (
              <div className="rounded-2xl border border-dashed border-gray-200 bg-white text-center py-12 px-6 text-sm text-gray-400">
                No content added yet. Use the API to populate your resume sections.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
