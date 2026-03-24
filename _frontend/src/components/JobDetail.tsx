import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobApi } from '../api/client'
import type { Job } from '../types'
import { SkeletonLoader } from './SkeletonLoader'

export const JobDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [job, setJob] = useState<Job | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchJobDetail = async () => {
      if (!id) {
        setError('Job ID not provided')
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setError(null)
        const response = await jobApi.getJob(id)
        setJob(response)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch job details'
        setError(errorMessage)
        setJob(null)
      } finally {
        setIsLoading(false)
      }
    }

    fetchJobDetail()
  }, [id])

  const handleBack = () => {
    navigate(-1)
  }

  const formatSalary = (min: number | null | undefined, max: number | null | undefined) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const postedDate = job
    ? new Date(job.posted_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : ''

  const salaryRange = job ? formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined) : null

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-textPrimary">💼 JobSync</h1>
            <p className="text-textSecondary mt-1">View job details</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back Button */}
        <button
          onClick={handleBack}
          className="mb-6 flex items-center text-primary hover:text-primaryHover font-medium transition"
        >
          <span className="text-xl mr-2">←</span>
          Back to Jobs
        </button>

        {/* Loading State */}
        {isLoading && <SkeletonLoader />}

        {/* Error State */}
        {error && !isLoading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 font-medium">Error loading job details</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
            <button
              onClick={handleBack}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              Go Back
            </button>
          </div>
        )}

        {/* Job Details */}
        {job && !isLoading && (
          <div className="space-y-6">
            {/* Header Section */}
            <div className="card p-8">
              {/* Title and Company */}
              <div className="mb-6">
                <h1 className="text-4xl font-bold text-textPrimary mb-2">{job.title}</h1>
                <p className="text-xl text-primary font-semibold">{job.company.name}</p>
              </div>

              {/* Meta Information */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-6 border-t border-border">
                {/* Location */}
                <div>
                  <p className="text-textSecondary text-sm font-medium mb-1">📍 Location</p>
                  <p className="text-textPrimary font-semibold">{job.location}</p>
                </div>

                {/* Remote */}
                <div>
                  <p className="text-textSecondary text-sm font-medium mb-1">💻 Work Mode</p>
                  <p className="text-textPrimary font-semibold">
                    {job.is_remote ? 'Remote' : 'On-site'}
                  </p>
                </div>

                {/* Experience Level */}
                {job.experience_level && (
                  <div>
                    <p className="text-textSecondary text-sm font-medium mb-1">📊 Experience</p>
                    <p className="text-textPrimary font-semibold capitalize">{job.experience_level}</p>
                  </div>
                )}

                {/* Salary */}
                {salaryRange && (
                  <div>
                    <p className="text-textSecondary text-sm font-medium mb-1">💰 Salary</p>
                    <p className="text-textPrimary font-semibold">{salaryRange}</p>
                  </div>
                )}

                {/* Posted Date */}
                {!salaryRange && (
                  <div>
                    <p className="text-textSecondary text-sm font-medium mb-1">📅 Posted</p>
                    <p className="text-textPrimary font-semibold">{postedDate}</p>
                  </div>
                )}
              </div>

              {salaryRange && (
                <div className="mt-6 pt-6 border-t border-border">
                  <p className="text-textSecondary text-sm font-medium mb-1">📅 Posted</p>
                  <p className="text-textPrimary font-semibold">{postedDate}</p>
                </div>
              )}
            </div>

            {/* Description Section */}
            <div className="card p-8">
              <h2 className="text-2xl font-bold text-textPrimary mb-4">Job Description</h2>
              <div className="prose prose-sm max-w-none">
                <p className="text-textPrimary whitespace-pre-wrap leading-relaxed">
                  {job.description}
                </p>
              </div>
            </div>

            {/* Skills Section */}
            {job.skills && job.skills.length > 0 && (
              <div className="card p-8">
                <h2 className="text-2xl font-bold text-textPrimary mb-4">Required Skills</h2>
                <div className="flex flex-wrap gap-3">
                  {job.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-primaryLight text-primary font-medium text-sm rounded-full hover:bg-primary transition"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Apply Section */}
            <div className="card p-8">
              <h2 className="text-2xl font-bold text-textPrimary mb-4">Ready to Apply?</h2>
              <p className="text-textSecondary mb-6">
                Click the button below to visit the company's application page.
              </p>
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary bg-success hover:bg-green-700"
              >
                🚀 Apply Now
              </a>
              <p className="text-textSecondary text-sm mt-4">
                You'll be redirected to the company's careers page
              </p>
            </div>

            {/* Additional Information */}
            <div className="bg-primaryLight border border-primary rounded-lg p-6 text-sm text-textPrimary">
              <p>
                <strong>Need help?</strong> Visit our{' '}
                <a href="/" className="text-primary hover:text-primaryHover">
                  job listings
                </a>{' '}
                to find more opportunities or use our search and filters to narrow down your options.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-border mt-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-textSecondary text-sm">
          <p>&copy; 2026 JobSync. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
