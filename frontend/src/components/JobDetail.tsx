import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobApi } from '../api/client'
import type { Job } from '../types'
import { SkeletonLoader } from './SkeletonLoader'
import { SaveButton } from './SaveButton'

interface JobDetailProps {
  job?: Job
  isEmbedded?: boolean
}

export const JobDetail: React.FC<JobDetailProps> = ({ job: propJob, isEmbedded = false }) => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [job, setJob] = useState<Job | null>(propJob || null)
  const [isLoading, setIsLoading] = useState(!propJob)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // If job is passed as prop, use it directly
    if (propJob) {
      setJob(propJob)
      setIsLoading(false)
      return
    }

    // Otherwise fetch by ID
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
  }, [id, propJob])

  const handleBack = () => {
    if (!isEmbedded) {
      navigate(-1)
    }
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

  if (isEmbedded) {
    return (
      <div className="h-full flex flex-col">
        {/* Loading State */}
        {isLoading && <SkeletonLoader />}

        {/* Error State */}
        {error && !isLoading && (
          <div className="p-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <p className="text-red-800 font-medium">Error loading job details</p>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Job Details */}
        {job && !isLoading && (
          <div className="flex-1 overflow-y-auto">
            {/* Header Section */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">{job.title}</h1>
                  <p className="text-lg text-blue-600 font-semibold">{job.company.name}</p>
                </div>
                <SaveButton jobId={job.job_id} size="lg" />
              </div>

              {/* Meta Information */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="mr-2">ðŸ“</span>
                  {job.location}
                </div>
                {job.is_remote && (
                  <div className="flex items-center text-sm text-green-600">
                    <span className="mr-2">ðŸ’»</span>
                    Remote
                  </div>
                )}
                {job.experience_level && (
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-2">ðŸ“Š</span>
                    {job.experience_level}
                  </div>
                )}
                {salaryRange && (
                  <div className="flex items-center text-sm text-green-600 font-medium">
                    <span className="mr-2">ðŸ’°</span>
                    {salaryRange}
                  </div>
                )}
              </div>

              <div className="text-sm text-gray-500 mb-4">
                Posted {postedDate}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <a
                  href={job.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-center font-medium"
                >
                  ðŸš€ Apply Now
                </a>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                  ðŸ’¾ Save Job
                </button>
              </div>
            </div>

            {/* Description Section */}
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Job Description</h2>
              <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
                {job.description.split('\n').map((paragraph, index) => (
                  <p key={index} className="mb-3">{paragraph}</p>
                ))}
              </div>
            </div>

            {/* Skills Section */}
            {job.skills && job.skills.length > 0 && (
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Required Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {job.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-2 bg-blue-100 text-blue-700 font-medium text-sm rounded-lg hover:bg-blue-200 transition-colors"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Similar Jobs Section */}
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Similar Jobs</h2>
              <div className="space-y-3">
                <div className="text-center py-8 text-gray-500">
                  <div className="text-3xl mb-2">ðŸ”</div>
                  <p>Similar jobs will appear here</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Original full-page layout for standalone job detail pages
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-textPrimary">ðŸ’¼ JobSync</h1>
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
          <span className="text-xl mr-2">â†</span>
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
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <h1 className="text-4xl font-bold text-textPrimary mb-2">{job.title}</h1>
                  <p className="text-xl text-primary font-semibold">{job.company.name}</p>
                </div>
                <SaveButton jobId={job.job_id} size="lg" />
              </div>

              {/* Meta Information */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-6 border-t border-border">
                {/* Location */}
                <div>
                  <p className="text-textSecondary text-sm font-medium mb-1">ðŸ“ Location</p>
                  <p className="text-textPrimary font-semibold">{job.location}</p>
                </div>

                {/* Remote */}
                <div>
                  <p className="text-textSecondary text-sm font-medium mb-1">ðŸ’» Work Mode</p>
                  <p className="text-textPrimary font-semibold">
                    {job.is_remote ? 'Remote' : 'On-site'}
                  </p>
                </div>

                {/* Experience Level */}
                {job.experience_level && (
                  <div>
                    <p className="text-textSecondary text-sm font-medium mb-1">ðŸ“Š Experience</p>
                    <p className="text-textPrimary font-semibold capitalize">{job.experience_level}</p>
                  </div>
                )}

                {/* Salary */}
                {salaryRange && (
                  <div>
                    <p className="text-textSecondary text-sm font-medium mb-1">ðŸ’° Salary</p>
                    <p className="text-textPrimary font-semibold">{salaryRange}</p>
                  </div>
                )}

                {/* Posted Date */}
                {!salaryRange && (
                  <div>
                    <p className="text-textSecondary text-sm font-medium mb-1">ðŸ“… Posted</p>
                    <p className="text-textPrimary font-semibold">{postedDate}</p>
                  </div>
                )}
              </div>

              {salaryRange && (
                <div className="mt-6 pt-6 border-t border-border">
                  <p className="text-textSecondary text-sm font-medium mb-1">ðŸ“… Posted</p>
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
                ðŸš€ Apply Now
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

