import React from 'react'
import type { Job } from '../types'
import { SaveButton } from './SaveButton'

interface JobCardProps {
  job: Job
  isSelected?: boolean
  onClick?: () => void
}

export const JobCard: React.FC<JobCardProps> = ({ job, isSelected = false, onClick }) => {
  const postedDate = new Date(job.posted_date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })

  const truncateDescription = (text: string, length: number = 120) => {
    return text.length > length ? text.substring(0, length) + '...' : text
  }

  const formatSalary = (min: number | null | undefined, max: number | null | undefined) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const salaryRange = formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined)

  return (
    <div
      className={`p-4 cursor-pointer transition-all duration-200 hover:bg-gray-50 ${
        isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : 'border-l-4 border-transparent'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate hover:text-blue-600 transition-colors">
            {job.title}
          </h3>
          <p className="text-base text-blue-600 font-medium truncate">{job.company.name}</p>
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <SaveButton jobId={job.job_id} size="sm" />
          {isSelected && (
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          )}
        </div>
      </div>

      {/* Location and Meta Info */}
      <div className="flex flex-wrap items-center gap-3 mb-3 text-sm text-gray-600">
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
        {job.experience_level && (
          <span className="flex items-center">
            <span className="mr-1">📊</span>
            {job.experience_level}
          </span>
        )}
        {salaryRange && (
          <span className="flex items-center text-green-600 font-medium">
            <span className="mr-1">💰</span>
            {salaryRange}
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-gray-700 text-sm mb-3 leading-relaxed">
        {truncateDescription(job.description)}
      </p>

      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {job.skills.slice(0, 3).map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-md font-medium"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                +{job.skills.length - 3}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Posted {postedDate}</span>
        <div className="flex items-center space-x-2">
          <span className="text-gray-400">•</span>
          <span>Match: {Math.round(job.score * 100)}%</span>
        </div>
      </div>
    </div>
  )
}
