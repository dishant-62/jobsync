import React from 'react'
import type { Job } from '../types'
import { JobCard } from './JobCard'

interface JobListProps {
  jobs: Job[]
  isLoading: boolean
  error?: string | null
  selectedJob: Job | null
  onJobSelect: (job: Job) => void
  onPageChange: (page: number) => void
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

export const JobList: React.FC<JobListProps> = ({
  jobs,
  isLoading,
  error,
  selectedJob,
  onJobSelect,
  onPageChange,
  total,
  page,
  pageSize,
  hasMore
}) => {
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold mb-2">Error</h3>
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (isLoading && jobs.length === 0) {
    return (
      <div className="p-6">
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 rounded-lg h-32"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (jobs.length === 0 && !isLoading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
          <p className="text-gray-500">Try adjusting your search criteria or filters</p>
        </div>
      </div>
    )
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="divide-y divide-gray-100">
      {jobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          isSelected={selectedJob?.id === job.id}
          onClick={() => onJobSelect(job)}
        />
      ))}

      {/* Load More Button */}
      {hasMore && !isLoading && (
        <div className="p-4 text-center">
          <button
            onClick={() => onPageChange(page + 1)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Load More Jobs
          </button>
        </div>
      )}

      {/* Loading indicator for pagination */}
      {isLoading && jobs.length > 0 && (
        <div className="p-4 text-center">
          <div className="inline-flex items-center text-gray-500 text-sm">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Loading more jobs...
          </div>
        </div>
      )}

      {/* End of results */}
      {!hasMore && jobs.length > 0 && (
        <div className="p-4 text-center text-gray-500 text-sm">
          You've reached the end of the results
        </div>
      )}
    </div>
  )
}
