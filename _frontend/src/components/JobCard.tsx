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

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      <div className="mb-3">
        <h3 className="text-xl font-semibold text-gray-900 mb-1">{job.title}</h3>
        <p className="text-sm text-gray-600">
          📍 {job.location}
        </p>
      </div>

      <p className="text-gray-700 text-sm mb-4">
        {truncateDescription(job.description)}
      </p>

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
