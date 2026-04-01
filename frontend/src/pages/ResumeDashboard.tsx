import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeApi } from '../services/resumeApi'
import { useAuth } from '../context/AuthContext'
import { ResumeCard } from '../components/resume/ResumeCard'
import type { ResumeListItem } from '../types/resume'

const MAX_SLOTS = 5

function AddResumeModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: (resume: ResumeListItem) => void
}) {
  const [title, setTitle] = useState('')
  const [target, setTarget] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    setLoading(true)
    setError(null)
    try {
      const { resume } = await resumeApi.create({ title: title.trim(), target_job_title: target.trim() || undefined })
      onCreated(resume as unknown as ResumeListItem)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create resume')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-modal-in">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-gray-900">Add Resume</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resume name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Software Engineer Resume"
              className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-black/20"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target job title <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="e.g. Senior Frontend Engineer"
              className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-black/20"
            />
          </div>
          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-full border border-gray-200 py-2.5 text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !title.trim()}
              className="flex-1 rounded-full bg-black text-white py-2.5 text-sm font-medium hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating…' : 'Create Resume'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function ResumeDashboard() {
  const navigate = useNavigate()
  const { user, isInitialising } = useAuth()
  const [resumes, setResumes] = useState<ResumeListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)

  // Redirect if not logged in
  useEffect(() => {
    if (!isInitialising && !user) navigate('/')
  }, [isInitialising, user, navigate])

  useEffect(() => {
    if (!user) return
    setLoading(true)
    resumeApi.list()
      .then(({ resumes: list }) => setResumes(list))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [user])

  async function handleDelete(id: string) {
    try {
      await resumeApi.remove(id)
      setResumes((prev) => prev.filter((r) => r._id !== id))
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  async function handleSetPrimary(id: string) {
    try {
      await resumeApi.setPrimary(id)
      setResumes((prev) =>
        prev.map((r) => ({ ...r, is_primary: r._id === id }))
      )
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Failed to set primary')
    }
  }

  function handleCreated(resume: ResumeListItem) {
    setResumes((prev) => [resume, ...prev])
    setShowAddModal(false)
    navigate(`/resume/${resume._id}`)
  }

  const slotsUsed = resumes.length

  if (isInitialising || (loading && !resumes.length)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-black border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Resume AI</h1>
            <p className="text-sm text-gray-400 mt-0.5">
              {slotsUsed} of {MAX_SLOTS} resume slots used
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            disabled={slotsUsed >= MAX_SLOTS}
            className="flex items-center gap-2 rounded-full bg-black text-white px-5 py-2.5 text-sm font-medium hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Resume
          </button>
        </div>

        {/* Slot bar */}
        <div className="mb-8">
          <div className="flex gap-1.5 mt-3">
            {Array.from({ length: MAX_SLOTS }).map((_, i) => (
              <div
                key={i}
                className={`h-1.5 flex-1 rounded-full transition-colors ${
                  i < slotsUsed ? 'bg-black' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          {slotsUsed >= MAX_SLOTS && (
            <p className="text-xs text-amber-600 mt-2">
              Maximum of {MAX_SLOTS} resumes reached. Delete one to add a new resume.
            </p>
          )}
        </div>

        {/* Error state */}
        {error && (
          <div className="mb-6 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3">
            {error}
          </div>
        )}

        {/* Table */}
        {resumes.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-gray-200 bg-white text-center py-16 px-6">
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-gray-600 font-medium mb-1">No resumes yet</p>
            <p className="text-sm text-gray-400 mb-5">
              Add your first resume and get instant AI feedback.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="rounded-full bg-black text-white px-6 py-2.5 text-sm font-medium hover:bg-gray-800 transition-colors"
            >
              Add Resume
            </button>
          </div>
        ) : (
          <div className="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <th className="py-3 px-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider hidden sm:table-cell">
                    Status
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider hidden md:table-cell">
                    Score
                  </th>
                  <th className="py-3 px-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider hidden lg:table-cell">
                    Last modified
                  </th>
                  <th className="py-3 px-4" />
                </tr>
              </thead>
              <tbody>
                {resumes.map((resume) => (
                  <ResumeCard
                    key={resume._id}
                    resume={resume}
                    onSelect={(id) => navigate(`/resume/${id}`)}
                    onDelete={handleDelete}
                    onSetPrimary={handleSetPrimary}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showAddModal && (
        <AddResumeModal onClose={() => setShowAddModal(false)} onCreated={handleCreated} />
      )}
    </div>
  )
}
