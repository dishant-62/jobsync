import React from 'react'

interface TopBarProps {
  totalJobs: number
  isLoading: boolean
  searchQuery: string
  onSearchChange: (query: string) => void
  activeFiltersCount: number
}

export const TopBar: React.FC<TopBarProps> = ({
  totalJobs,
  isLoading,
  searchQuery,
  onSearchChange,
  activeFiltersCount
}) => {
  return (
    <div className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-900">💼 JobSync</h1>
          </div>

          {/* Global Search */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search jobs, companies, or keywords..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              {isLoading ? (
                <span className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  Searching...
                </span>
              ) : (
                <span>
                  {totalJobs.toLocaleString()} jobs found
                  {activeFiltersCount > 0 && (
                    <span className="ml-2 text-blue-600 font-medium">
                      ({activeFiltersCount} filter{activeFiltersCount !== 1 ? 's' : ''} active)
                    </span>
                  )}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}