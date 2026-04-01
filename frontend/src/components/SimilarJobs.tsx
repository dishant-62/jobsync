import React from 'react'
import type { Job } from '../types'
import { JobCard } from './JobCard'

interface SimilarJobsProps {
  jobs: Job[]
  isLoading?: boolean
  onJobSelect?: (job: Job) => void
}

export const SimilarJobs: React.FC<SimilarJobsProps> = ({
  jobs,
  isLoading = false,
  onJobSelect
}) => {
  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="flex space-x-4 overflow-x-auto pb-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex-shrink-0 w-64">
              <div className="animate-pulse">
                <div className="bg-gray-200 rounded-lg h-32"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (jobs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-3xl mb-2">🔍</div>
        <p className="text-sm">No similar jobs found</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex space-x-4 overflow-x-auto pb-2 scrollbar-hide">
        {jobs.map((job) => (
          <div key={job.id} className="flex-shrink-0 w-64">
            <JobCard
              job={job}
              variant="compact"
              onClick={() => onJobSelect?.(job)}
              enableNavigation={false}
            />
          </div>
        ))}
      </div>
    </div>
  )
}