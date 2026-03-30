import { useState, useEffect, useCallback } from 'react'
import { TopBar } from '../components/TopBar'
import { FiltersPanel } from '../components/FiltersPanel'
import { JobList } from '../components/JobList'
import { JobDetailPanel } from '../components/JobDetailPanel'
import { jobApi } from '../api/client'
import type { Job } from '../types'

function JobsList() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filtersCollapsed, setFiltersCollapsed] = useState(false)

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('')
  const [isRemote, setIsRemote] = useState(false)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [hasMore, setHasMore] = useState(false)

  // Fetch jobs on component mount and when filters/pagination changes
  const fetchJobs = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      console.log(`🔍 DEBUG: Fetching jobs - page: ${page}, page_size: ${pageSize}, q: "${searchQuery}", location: "${location}", experience_level: "${experienceLevel}", is_remote: ${isRemote}`)

      const response = await jobApi.listJobs({
        q: searchQuery,
        location: location || undefined,
        experience_level: experienceLevel || undefined,
        is_remote: isRemote ? true : undefined,
        skills: selectedSkills.length > 0 ? selectedSkills : undefined,
        page,
        page_size: pageSize,
      })

      console.log(`🔍 DEBUG: Response received - total: ${response.total}, jobs returned: ${response.jobs.length}, has_more: ${response.has_more}, page: ${response.page}, page_size: ${response.page_size}`)

      setJobs(response.jobs)
      setTotal(response.total)
      setHasMore(response.has_more)

      // Auto-select first job if none selected and jobs exist
      if (response.jobs.length > 0 && !selectedJob) {
        setSelectedJob(response.jobs[0])
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch jobs'
      setError(errorMessage)
      setJobs([])
      setTotal(0)
    } finally {
      setIsLoading(false)
    }
  }, [searchQuery, location, experienceLevel, isRemote, selectedSkills, page, pageSize, selectedJob])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const handleSearch = (query: string) => {
    console.log(`🔍 DEBUG: Search changed to: "${query}" - resetting to page 1`)
    setSearchQuery(query)
    setPage(1) // Reset to first page
    setSelectedJob(null) // Clear selected job
  }

  const handleFiltersChange = (filters: {
    location: string
    experience_level: string
    is_remote: boolean
    skills: string[]
  }) => {
    console.log(`🔍 DEBUG: Filters changed - location: "${filters.location}", experience_level: "${filters.experience_level}", is_remote: ${filters.is_remote}, skills: [${filters.skills.join(', ')}] - resetting to page 1`)
    setLocation(filters.location)
    setExperienceLevel(filters.experience_level)
    setIsRemote(filters.is_remote)
    setSelectedSkills(filters.skills)
    setPage(1) // Reset to first page
    setSelectedJob(null) // Clear selected job
  }

  const handleJobSelect = (job: Job) => {
    setSelectedJob(job)
  }

  const handlePageChange = (newPage: number) => {
    console.log(`🔍 DEBUG: Page changed from ${page} to ${newPage}`)
    setPage(newPage)
    setSelectedJob(null) // Clear selected job
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleToggleFilters = () => {
    setFiltersCollapsed(!filtersCollapsed)
  }

  // Calculate active filters count
  const activeFiltersCount = [
    searchQuery,
    location,
    experienceLevel,
    isRemote,
    ...selectedSkills
  ].filter(Boolean).length

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Bar */}
      <TopBar
        totalJobs={total}
        isLoading={isLoading}
        searchQuery={searchQuery}
        onSearchChange={handleSearch}
        activeFiltersCount={activeFiltersCount}
      />

      {/* Main Content - 3 Column Layout */}
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Filters Panel - Left Column */}
        <FiltersPanel
          onFiltersChange={handleFiltersChange}
          isLoading={isLoading}
          isCollapsed={filtersCollapsed}
          onToggleCollapse={handleToggleFilters}
        />

        {/* Job List - Center Column */}
        <div className={`flex-1 ${!filtersCollapsed ? 'lg:w-2/5 xl:w-2/5' : 'lg:w-1/2 xl:w-1/2'} bg-white border-r border-gray-200`}>
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-white">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Jobs
                  {total > 0 && (
                    <span className="text-gray-500 font-normal ml-2">
                      ({total.toLocaleString()})
                    </span>
                  )}
                </h2>
                {activeFiltersCount > 0 && (
                  <p className="text-sm text-gray-600 mt-1">
                    {activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} applied
                  </p>
                )}
              </div>

              {/* Mobile Filter Toggle */}
              <button
                onClick={handleToggleFilters}
                className="lg:hidden p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title={filtersCollapsed ? "Show filters" : "Hide filters"}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </button>
            </div>

            {/* Job List Content */}
            <div className="flex-1 overflow-y-auto">
              <JobList
                jobs={jobs}
                isLoading={isLoading}
                error={error}
                selectedJob={selectedJob}
                onJobSelect={handleJobSelect}
                onPageChange={handlePageChange}
                page={page}
                hasMore={hasMore}
              />
            </div>
          </div>
        </div>

        {/* Job Detail Panel - Right Column */}
        <div className={`hidden lg:block ${!filtersCollapsed ? 'lg:w-2/5 xl:w-2/5' : 'lg:w-1/2 xl:w-1/2'} bg-white`}>
          <JobDetailPanel selectedJob={selectedJob} />
        </div>
      </div>

      {/* Mobile Job Detail Modal */}
      {selectedJob && (
        <div className="lg:hidden fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Job Details</h2>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
              <JobDetailPanel selectedJob={selectedJob} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default JobsList
