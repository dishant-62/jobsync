import React, { useState, useEffect } from 'react'

interface SearchBarProps {
  onSearch: (query: string) => void
  isLoading?: boolean
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading = false }) => {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  // Debounce search query (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  // Trigger search when debounced query changes
  useEffect(() => {
    onSearch(debouncedQuery)
  }, [debouncedQuery, onSearch])

  return (
    <div className="mb-6 card p-6">
      <div>
        <label htmlFor="search" className="block text-sm font-medium text-textSecondary mb-2">
          🔍 Search Jobs
        </label>
        <input
          id="search"
          type="text"
          placeholder="Search by title, company, or keywords..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isLoading}
          className="w-full input-base disabled:bg-gray-100"
        />
      </div>
    </div>
  )
}

