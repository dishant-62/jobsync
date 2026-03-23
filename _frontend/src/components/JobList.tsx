import React from 'react'
import type { Job } from '../types'
import { JobCard } from './JobCard'

interface JobListProps {
  jobs: Job[]
  isLoading: boolean
  error?: string | null
}

export const JobList: React.FC<JobListProps> = ({ jobs, isLoading, error }) => {
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-textPrimary font-semibold mb-2">Error</h3>
        <p className="text-red-800">{error}</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-textSecondary text-lg">No jobs found. Try adjusting your search.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  )
}
