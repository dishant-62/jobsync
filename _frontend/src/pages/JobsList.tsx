import { useState, useEffect, useCallback } from 'react'
import { SearchBar } from '../components/SearchBar'
import { FiltersPanel } from '../components/FiltersPanel'
import { JobList } from '../components/JobList'
import { JobDetail } from '../components/JobDetail'
import { jobApi } from '../api/client'
import type { Job } from '../types'

function JobsList() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                💼 JobSync
              </h1>
              <p className="text-gray-600 text-sm">Discover your next opportunity</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                {total > 0 && (
                  <span>{total.toLocaleString()} jobs found</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Search and Filters Bar */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} isLoading={isLoading} />
            </div>
            <div className="lg:w-80">
              <FiltersPanel onFiltersChange={handleFiltersChange} isLoading={isLoading} />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Split Screen Layout */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6 h-[calc(100vh-200px)]">
          {/* Left Panel - Job List (35%) */}
          <div className="w-full lg:w-2/5 xl:w-2/5 flex flex-col">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex-1 overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Jobs {total > 0 && <span className="text-gray-500 font-normal">({total.toLocaleString()})</span>}
                </h2>
              </div>
              <div className="flex-1 overflow-y-auto">
                <JobList
                  jobs={jobs}
                  isLoading={isLoading}
                  error={error}
                  selectedJob={selectedJob}
                  onJobSelect={handleJobSelect}
                  onPageChange={handlePageChange}
                  total={total}
                  page={page}
                  pageSize={pageSize}
                  hasMore={hasMore}
                />
              </div>
            </div>
          </div>

          {/* Right Panel - Job Details (65%) */}
          <div className="hidden lg:block lg:w-3/5 xl:w-3/5">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full overflow-hidden">
              {selectedJob ? (
                <JobDetail job={selectedJob} isEmbedded={true} />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <div className="text-6xl mb-4">💼</div>
                    <h3 className="text-xl font-medium mb-2">Select a job to view details</h3>
                    <p className="text-gray-400">Choose a job from the list to see full information</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Mobile Job Detail Modal/Overlay */}
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
              <JobDetail job={selectedJob} isEmbedded={true} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default JobsList
