import { Link } from 'react-router-dom'
import type { Job } from '../types'

interface FeaturedJobsProps {
  jobs: Job[]
  isLoading: boolean
}

export const FeaturedJobs: React.FC<FeaturedJobsProps> = ({ jobs, isLoading }) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="card p-6">
            <div className="space-y-3">
              <div className="h-6 bg-border rounded w-3/4 animate-pulse"></div>
              <div className="h-4 bg-border rounded w-1/2 animate-pulse"></div>
              <div className="h-4 bg-border rounded w-1/3 animate-pulse"></div>
              <div className="flex gap-2 mt-4">
                <div className="h-6 bg-border rounded-full w-16 animate-pulse"></div>
                <div className="h-6 bg-border rounded-full w-20 animate-pulse"></div>
              </div>
              <div className="h-10 bg-border rounded mt-4 animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {jobs.map((job) => (
        <div
          key={job.id}
          className="card p-6 hover:scale-105 hover:shadow-lg transition-all duration-200"
        >
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-textPrimary mb-2 line-clamp-2">
              {job.title}
            </h3>
            <p className="text-textSecondary font-medium">
              {job.company.name}
            </p>
            <p className="text-sm text-textSecondary">
              📍 {job.location}
            </p>
          </div>

          {job.skills && job.skills.length > 0 && (
            <div className="mb-4">
              <div className="flex flex-wrap gap-2">
                {job.skills.slice(0, 3).map((skill, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-primaryLight text-primary text-xs rounded-full"
                  >
                    {skill}
                  </span>
                ))}
                {job.skills.length > 3 && (
                  <span className="px-3 py-1 bg-card text-textSecondary text-xs rounded-full">
                    +{job.skills.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}

          <Link
            to={`/jobs/${job.id}`}
            className="btn-primary w-full text-center"
          >
            View Details
          </Link>
        </div>
      ))}
    </div>
  )
}