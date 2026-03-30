import React from 'react'
import { useNavigate } from 'react-router-dom'
import type { Job } from '../types'
import { SaveButton } from './SaveButton'

interface JobCardProps {
  job: Job
  isSelected?: boolean
  onClick?: () => void
  enableNavigation?: boolean
  variant?: 'default' | 'compact' // For different contexts
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  isSelected = false,
  onClick,
  enableNavigation = true,
  variant = 'default'
}) => {
  const navigate = useNavigate()

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

  const handleClick = () => {
    if (enableNavigation) {
      navigate(`/jobs/${job.job_id}`)
    } else if (onClick) {
      onClick()
    }
  }

  const salaryRange = formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined)

  if (variant === 'compact') {
    return (
      <div
        className={`p-3 cursor-pointer transition-all duration-200 hover:shadow-md rounded-lg border ${
          isSelected
            ? 'bg-blue-50 border-blue-300 shadow-sm'
            : 'bg-white border-gray-200 hover:border-gray-300'
        }`}
        onClick={handleClick}
      >
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-gray-900 truncate mb-1">
              {job.title}
            </h4>
            <p className="text-xs text-blue-600 font-medium truncate">
              {job.company.name}
            </p>
          </div>
          <SaveButton jobId={job.job_id} size="sm" />
        </div>

        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>📍 {job.location}</span>
          {job.is_remote && <span>• 💻 Remote</span>}
        </div>

        <div className="mt-2 text-xs text-gray-400">
          {formatPostedDate(job.posted_date)}
        </div>
      </div>
    )
  }

  return (
    <div
      className={`p-6 cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.01] rounded-xl border ${
        isSelected
          ? 'bg-blue-50 border-blue-300 shadow-md'
          : 'bg-white border-gray-200 hover:border-gray-300'
      }`}
      onClick={handleClick}
    >
      {/* Header Section */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-gray-900 mb-2 leading-tight hover:text-blue-600 transition-colors">
            {job.title}
          </h3>
          <div className="flex items-center gap-2 mb-2">
            <p className="text-base text-blue-600 font-semibold truncate">
              {job.company.name}
            </p>
            {job.is_remote && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 font-medium">
                <span className="mr-1">💻</span>
                Remote
              </span>
            )}
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-1">📍</span>
            <span className="truncate">{job.location}</span>
          </div>
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <SaveButton jobId={job.job_id} size="sm" />
          {isSelected && (
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          )}
        </div>
      </div>

      {/* Meta Information */}
      <div className="flex flex-wrap items-center gap-3 mb-4 text-sm">
        {job.experience_level && (
          <span className="inline-flex items-center px-3 py-1 rounded-full bg-gray-100 text-gray-700 font-medium">
            <span className="mr-1">📊</span>
            {job.experience_level}
          </span>
        )}
        {salaryRange && (
          <span className="inline-flex items-center px-3 py-1 rounded-full bg-green-100 text-green-800 font-medium">
            <span className="mr-1">💰</span>
            {salaryRange}
          </span>
        )}
      </div>

      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {job.skills.slice(0, 4).map((skill, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-blue-50 text-blue-700 font-medium border border-blue-200"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 4 && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-gray-100 text-gray-600 font-medium">
                +{job.skills.length - 4} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Description Preview */}
      <p className="text-sm text-gray-600 leading-relaxed mb-4 line-clamp-2">
        {job.description.length > 150
          ? `${job.description.substring(0, 150)}...`
          : job.description
        }
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center">
          <span className="mr-3">🕒 {formatPostedDate(job.posted_date)}</span>
          <span className="text-gray-400">•</span>
          <span className="ml-3">Match: {Math.round(job.score * 100)}%</span>
        </div>
        <div className="text-blue-600 font-medium hover:text-blue-700 transition-colors">
          View details →
        </div>
      </div>
    </div>
  )
}
