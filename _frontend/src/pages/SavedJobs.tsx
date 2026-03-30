import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { jobApi } from '../api/client'
import { JobList } from '../components/JobList'
import type { Job } from '../types'

function SavedJobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch saved jobs on component mount
  const fetchSavedJobs = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await jobApi.getSavedJobs()
      setJobs(response.jobs)
      setTotal(response.total)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch saved jobs'
      setError(errorMessage)
      setJobs([])
      setTotal(0)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSavedJobs()
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-textPrimary">⭐ Saved Jobs</h1>
              <p className="text-textSecondary mt-1">
                {total > 0 ? `You have ${total} saved job${total !== 1 ? 's' : ''}` : 'No saved jobs yet'}
              </p>
            </div>
            <Link
              to="/jobs"
              className="btn-primary"
            >
              Browse Jobs
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {jobs.length === 0 && !isLoading && !error && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">⭐</div>
            <h2 className="text-2xl font-bold text-textPrimary mb-2">No saved jobs yet</h2>
            <p className="text-textSecondary mb-6">
              Start saving jobs you're interested in to view them here later.
            </p>
            <Link
              to="/jobs"
              className="btn-primary"
            >
              Browse Available Jobs
            </Link>
          </div>
        )}

        <JobList
          jobs={jobs}
          isLoading={isLoading}
          error={error}
        />
      </main>
    </div>
  )
}

export default SavedJobs