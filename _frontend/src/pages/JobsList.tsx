import { useState, useEffect, useCallback } from 'react'
import { SearchBar } from '../components/SearchBar'
import { FiltersPanel } from '../components/FiltersPanel'
import { JobList } from '../components/JobList'
import { Pagination } from '../components/Pagination'
import { jobApi } from '../api/client'
import type { Job } from '../types'

function JobsList() {
  const [jobs, setJobs] = useState<Job[]>([])
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
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch jobs'
      setError(errorMessage)
      setJobs([])
      setTotal(0)
    } finally {
      setIsLoading(false)
    }
  }, [searchQuery, location, experienceLevel, isRemote, selectedSkills, page, pageSize])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const handleSearch = (query: string) => {
    console.log(`🔍 DEBUG: Search changed to: "${query}" - resetting to page 1`)
    setSearchQuery(query)
    setPage(1) // Reset to first page
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
  }

  const handlePageChange = (newPage: number) => {
    console.log(`🔍 DEBUG: Page changed from ${page} to ${newPage}`)
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-textPrimary">
              💼 JobSync
            </h1>
            <p className="text-textSecondary mt-1">Discover your next opportunity</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {/* Filters Panel */}
        <FiltersPanel onFiltersChange={handleFiltersChange} isLoading={isLoading} />

        {/* Job Count */}
        {total > 0 && (
          <div className="mb-4 text-sm text-textSecondary">
            Found <span className="font-semibold text-textPrimary">{total}</span> job(s)
          </div>
        )}

        {/* Debug Info */}
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="text-sm font-semibold text-yellow-800 mb-2">🔍 Debug Info</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-yellow-700">Total Jobs:</span>
              <span className="ml-2 text-yellow-900">{total}</span>
            </div>
            <div>
              <span className="font-medium text-yellow-700">Loaded Jobs:</span>
              <span className="ml-2 text-yellow-900">{jobs.length}</span>
            </div>
            <div>
              <span className="font-medium text-yellow-700">Current Page:</span>
              <span className="ml-2 text-yellow-900">{page}</span>
            </div>
            <div>
              <span className="font-medium text-yellow-700">Total Pages:</span>
              <span className="ml-2 text-yellow-900">{total > 0 ? Math.ceil(total / pageSize) : 0}</span>
            </div>
            <div>
              <span className="font-medium text-yellow-700">Page Size:</span>
              <span className="ml-2 text-yellow-900">{pageSize}</span>
            </div>
            <div>
              <span className="font-medium text-yellow-700">Has More:</span>
              <span className={`ml-2 ${hasMore ? 'text-green-600' : 'text-red-600'}`}>
                {hasMore ? 'Yes' : 'No'}
              </span>
            </div>
            <div>
              <span className="font-medium text-yellow-700">Progress:</span>
              <span className="ml-2 text-yellow-900">
                {total > 0 ? `${Math.round((jobs.length / total) * 100)}%` : '0%'}
              </span>
            </div>
          </div>
        </div>

        {/* Job List */}
        <JobList jobs={jobs} isLoading={isLoading} error={error} />

        {/* Pagination */}
        <Pagination
          total={total}
          page={page}
          pageSize={pageSize}
          hasMore={hasMore}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-border mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-textSecondary text-sm">
            © 2026 JobSync. Powered by the JobSync Platform API.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default JobsList
