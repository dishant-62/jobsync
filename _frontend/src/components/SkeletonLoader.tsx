import React from 'react'

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="animate-pulse">
      {/* Header Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="h-7 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-5 bg-gray-200 rounded w-1/3"></div>
          </div>
          <div className="h-8 w-8 bg-gray-200 rounded"></div>
        </div>

        {/* Meta Information */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="h-4 bg-gray-200 rounded w-20"></div>
          <div className="h-4 bg-gray-200 rounded w-16"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
          <div className="h-4 bg-gray-200 rounded w-18"></div>
        </div>

        <div className="h-4 bg-gray-200 rounded w-16 mb-4"></div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <div className="h-10 bg-gray-200 rounded-lg flex-1"></div>
          <div className="h-10 bg-gray-200 rounded-lg w-24"></div>
        </div>
      </div>

      {/* Description Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="h-6 bg-gray-200 rounded w-32 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-4/5"></div>
        </div>
      </div>

      {/* Skills Section */}
      <div className="p-6 border-b border-gray-200">
        <div className="h-6 bg-gray-200 rounded w-24 mb-4"></div>
        <div className="flex flex-wrap gap-2">
          <div className="h-8 bg-gray-200 rounded-lg w-16"></div>
          <div className="h-8 bg-gray-200 rounded-lg w-20"></div>
          <div className="h-8 bg-gray-200 rounded-lg w-18"></div>
          <div className="h-8 bg-gray-200 rounded-lg w-22"></div>
          <div className="h-8 bg-gray-200 rounded-lg w-16"></div>
        </div>
      </div>

      {/* Similar Jobs Section */}
      <div className="p-6">
        <div className="h-6 bg-gray-200 rounded w-28 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  )
}

