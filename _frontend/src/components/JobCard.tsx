import React from 'react'
import { Link } from 'react-router-dom'
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

  const formatSalary = (min: number | null | undefined, max: number | null | undefined) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const salaryRange = formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined)

  return (
    <div className="card p-6 hover:shadow-lg transition cursor-pointer">
      {/* Clickable header area */}
      <Link to={`/jobs/${job.id}`} className="block hover:opacity-90 transition">
        <div className="mb-3">
          <h3 className="text-xl font-semibold text-textPrimary mb-1 hover:text-primary transition">
            {job.title}
          </h3>
          <p className="text-base text-primary font-medium">{job.company.name}</p>
        </div>

        {/* Location and Meta Info */}
        <div className="flex flex-wrap gap-3 mb-4 text-sm text-textSecondary">
          <span>📍 {job.location}</span>
          {job.is_remote && <span>💻 Remote</span>}
          {job.experience_level && <span>📊 {job.experience_level}</span>}
          {salaryRange && <span>💰 {salaryRange}</span>}
        </div>

        {/* Description */}
        <p className="text-textPrimary text-sm mb-4">
          {truncateDescription(job.description)}
        </p>
      </Link>

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
        <span className="text-xs text-textSecondary">
          Posted: {postedDate}
        </span>
        <div className="flex gap-2">
          <Link
            to={`/jobs/${job.id}`}
            className="btn-primary"
          >
            View Details
          </Link>
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary bg-success hover:bg-green-700"
          >
            Apply Now
          </a>
        </div>
      </div>
    </div>
  )
}
