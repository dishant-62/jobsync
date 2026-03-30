import React from 'react'

interface PaginationProps {
  total: number
  page: number
  pageSize: number
  hasMore: boolean
  onPageChange: (newPage: number) => void
  isLoading: boolean
}

export const Pagination: React.FC<PaginationProps> = ({
  total,
  page,
  pageSize,
  hasMore,
  onPageChange,
  isLoading,
}) => {
  const totalPages = Math.ceil(total / pageSize)

  const handlePrevious = () => {
    if (page > 1) {
      onPageChange(page - 1)
    }
  }

  const handleNext = () => {
    if (hasMore) {
      onPageChange(page + 1)
    }
  }

  if (total === 0) {
    return null
  }

  return (
    <div className="mt-8 flex items-center justify-between card p-4">
      <div className="text-sm text-textSecondary">
        Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} jobs
      </div>

      <div className="flex gap-2">
        <button
          onClick={handlePrevious}
          disabled={page === 1 || isLoading}
          className="px-4 py-2 border border-border rounded-lg text-sm font-medium text-textPrimary bg-white hover:bg-primaryLight disabled:bg-gray-100 disabled:text-textSecondary transition"
        >
          Previous
        </button>

        <span className="px-4 py-2 text-sm text-textPrimary">
          Page {page} of {totalPages}
        </span>

        <button
          onClick={handleNext}
          disabled={!hasMore || isLoading}
          className="px-4 py-2 border border-border rounded-lg text-sm font-medium text-textPrimary bg-white hover:bg-primaryLight disabled:bg-gray-100 disabled:text-textSecondary transition"
        >
          Next
        </button>
      </div>
    </div>
  )
}
