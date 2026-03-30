import React, { useState, useEffect } from 'react'
import type { Job } from '../types'
import { SkeletonLoader } from './SkeletonLoader'
import { SaveButton } from './SaveButton'

interface JobDetailPanelProps {
  selectedJob: Job | null
}

export const JobDetailPanel: React.FC<JobDetailPanelProps> = ({ selectedJob }) => {
  const [job, setJob] = useState<Job | null>(selectedJob)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (selectedJob) {
      // If we have the full job data, use it directly
      setJob(selectedJob)
      setIsLoading(false)
      setError(null)
    } else {
      // Clear the panel
      setJob(null)
      setIsLoading(false)
      setError(null)
    }
  }, [selectedJob])

  const formatSalary = (min: number | null | undefined, max: number | null | undefined) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const formatPostedDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 1) return '1 day ago'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return `${Math.floor(diffDays / 30)} months ago`
  }

  const salaryRange = job ? formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined) : null

  if (!job && !isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">💼</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a job to view details</h3>
          <p className="text-gray-500">Choose a job from the list to see full information</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="p-6 bg-white">
        <SkeletonLoader />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 bg-white">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-red-900 mb-2">Error loading job details</h3>
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (!job) return null

  return (
    <div className="bg-white h-full overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 mb-2 leading-tight">
              {job.title}
            </h1>
            <p className="text-lg text-blue-600 font-semibold mb-2">
              {job.company.name}
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span className="flex items-center">
                <span className="mr-1">📍</span>
                {job.location}
              </span>
              {job.is_remote && (
                <span className="flex items-center text-green-600">
                  <span className="mr-1">💻</span>
                  Remote
                </span>
              )}
            </div>
          </div>
          <SaveButton jobId={job.job_id} size="lg" />
        </div>

        {/* Meta Info */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {job.experience_level && (
            <div className="flex items-center p-3 bg-gray-50 rounded-lg">
              <span className="text-lg mr-3">📊</span>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Experience</p>
                <p className="text-sm font-semibold text-gray-900">{job.experience_level}</p>
              </div>
            </div>
          )}
          {salaryRange && (
            <div className="flex items-center p-3 bg-green-50 rounded-lg">
              <span className="text-lg mr-3">💰</span>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Salary</p>
                <p className="text-sm font-semibold text-green-800">{salaryRange}</p>
              </div>
            </div>
          )}
        </div>

        {/* Posted Date */}
        <div className="text-sm text-gray-500 mb-6">
          Posted {formatPostedDate(job.posted_date)}
        </div>

        {/* Apply Button */}
        <a
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center font-semibold text-lg shadow-sm hover:shadow-md"
        >
          🚀 Apply Now
        </a>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Skills */}
        {job.skills && job.skills.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Required Skills</h2>
            <div className="flex flex-wrap gap-2">
              {job.skills.map((skill, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-2 rounded-full text-sm bg-blue-50 text-blue-700 font-medium border border-blue-200"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Job Description */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Job Description</h2>
          <div className="prose prose-sm max-w-none">
            <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {job.description}
            </div>
          </div>
        </div>

        {/* Company Info */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">About {job.company.name}</h3>
          <p className="text-gray-600 text-sm">
            This position is with {job.company.name}. Visit their careers page to learn more about the company and explore other opportunities.
          </p>
        </div>

        {/* Similar Jobs Placeholder */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Similar Jobs</h2>
          <div className="space-y-3">
            <div className="text-center py-8 text-gray-500">
              <div className="text-3xl mb-2">🔍</div>
              <p className="text-sm">Similar jobs will appear here</p>
              <p className="text-xs text-gray-400 mt-1">Feature coming soon</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}