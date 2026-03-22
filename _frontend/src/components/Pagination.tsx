import React from 'react'

interface PaginationProps {
  total: number
  limit: number
  offset: number
  onPageChange: (newOffset: number) => void
  isLoading: boolean
}

export const Pagination: React.FC<PaginationProps> = ({
  total,
  limit,
  offset,
  onPageChange,
  isLoading,
}) => {
  const currentPage = Math.floor(offset / limit) + 1
  const totalPages = Math.ceil(total / limit)

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange((currentPage - 2) * limit)
    }
  }

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage * limit)
    }
  }

  if (total === 0) {
    return null
  }

  return (
    <div className="mt-8 flex items-center justify-between bg-white p-4 rounded-lg shadow">
      <div className="text-sm text-gray-600">
        Showing {offset + 1} to {Math.min(offset + limit, total)} of {total} jobs
      </div>

      <div className="flex gap-2">
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1 || isLoading}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 transition"
        >
          Previous
        </button>

        <span className="px-4 py-2 text-sm text-gray-700">
          Page {currentPage} of {totalPages}
        </span>

        <button
          onClick={handleNext}
          disabled={currentPage === totalPages || isLoading}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 transition"
        >
          Next
        </button>
      </div>
    </div>
  )
}
