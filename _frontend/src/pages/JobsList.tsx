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
      const response = await jobApi.listJobs({
        q: searchQuery,
        location: location || undefined,
        experience_level: experienceLevel || undefined,
        is_remote: isRemote ? true : undefined,
        skills: selectedSkills.length > 0 ? selectedSkills : undefined,
        page,
        page_size: pageSize,
      })
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
    setSearchQuery(query)
    setPage(1) // Reset to first page
  }

  const handleFiltersChange = (filters: {
    location: string
    experience_level: string
    is_remote: boolean
    skills: string[]
  }) => {
    setLocation(filters.location)
    setExperienceLevel(filters.experience_level)
    setIsRemote(filters.is_remote)
    setSelectedSkills(filters.skills)
    setPage(1) // Reset to first page
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

        {/* Job List */}
        <JobList jobs={jobs} isLoading={isLoading} error={error} />

        {/* Pagination */}
        <Pagination
          total={total}
          page={page}
          pageSize={pageSize}
          hasMore={hasMore}
          onPageChange={(newPage) => setPage(newPage)}
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
