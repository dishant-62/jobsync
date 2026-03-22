import React, { useState, useEffect, useCallback } from 'react'
import { SearchBar } from './components/SearchBar'
import { JobList } from './components/JobList'
import { Pagination } from './components/Pagination'
import { jobApi } from './api/client'
import type { Job } from './types'

function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [searchQuery, setSearchQuery] = useState('')
  const [searchLocation, setSearchLocation] = useState('')
  const [limit] = useState(20)
  const [offset, setOffset] = useState(0)

  // Fetch jobs on component mount and when search/pagination changes
  const fetchJobs = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await jobApi.listJobs(searchQuery, searchLocation, limit, offset)
      setJobs(response.jobs)
      setTotal(response.total)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch jobs'
      setError(errorMessage)
      setJobs([])
      setTotal(0)
    } finally {
      setIsLoading(false)
    }
  }, [searchQuery, searchLocation, limit, offset])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const handleSearch = (query: string, location: string) => {
    setSearchQuery(query)
    setSearchLocation(location)
    setOffset(0) // Reset to first page
  }

  const handlePageChange = (newOffset: number) => {
    setOffset(newOffset)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            💼 JobSync
          </h1>
          <p className="text-gray-600 mt-1">Discover your next opportunity</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {/* Job Count */}
        {total > 0 && (
          <div className="mb-4 text-sm text-gray-600">
            Found <span className="font-semibold">{total}</span> job(s)
          </div>
        )}

        {/* Job List */}
        <JobList jobs={jobs} isLoading={isLoading} error={error} />

        {/* Pagination */}
        <Pagination
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            © 2024 JobSync. Powered by the JobSync Platform API.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
