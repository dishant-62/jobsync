import React from 'react'
import type { Job } from '../types'

interface JobCardProps {
  job: Job
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const postedDate = new Date(job.posted_date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  const truncateDescription = (text: string, length: number = 200) => {
    return text.length > length ? text.substring(0, length) + '...' : text
  }

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const salaryRange = formatSalary(job.salary_min, job.salary_max)

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      {/* Header */}
      <div className="mb-3">
        <h3 className="text-xl font-semibold text-gray-900 mb-1">{job.title}</h3>
        <p className="text-base text-blue-600 font-medium">{job.company.name}</p>
      </div>

      {/* Location and Meta Info */}
      <div className="flex flex-wrap gap-3 mb-4 text-sm text-gray-600">
        <span>📍 {job.location}</span>
        {job.is_remote && <span>💻 Remote</span>}
        {job.experience_level && <span>📊 {job.experience_level}</span>}
        {salaryRange && <span>💰 {salaryRange}</span>}
      </div>

      {/* Description */}
      <p className="text-gray-700 text-sm mb-4">
        {truncateDescription(job.description)}
      </p>

      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-700 mb-2">Required Skills:</p>
          <div className="flex flex-wrap gap-2">
            {job.skills.slice(0, 5).map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 5 && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                +{job.skills.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">
          Posted: {postedDate}
        </span>
        <a
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition"
        >
          Apply Now
        </a>
      </div>
    </div>
  )
}
