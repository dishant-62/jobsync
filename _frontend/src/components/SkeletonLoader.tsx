import React from 'react'

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="space-y-4">
      {/* Skeleton for header */}
      <div className="card p-6">
        <div className="space-y-3">
          {/* Title skeleton */}
          <div className="h-8 bg-border rounded w-3/4 animate-pulse"></div>

          {/* Company skeleton */}
          <div className="h-5 bg-border rounded w-1/3 animate-pulse"></div>

          {/* Meta info skeleton */}
          <div className="flex gap-3 pt-2">
            <div className="h-4 bg-border rounded w-24 animate-pulse"></div>
            <div className="h-4 bg-border rounded w-20 animate-pulse"></div>
            <div className="h-4 bg-border rounded w-28 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Skeleton for description section */}
      <div className="card p-6">
        <div className="space-y-4">
          <div className="h-6 bg-border rounded w-1/4 animate-pulse"></div>
          <div className="space-y-2">
            <div className="h-4 bg-border rounded animate-pulse"></div>
            <div className="h-4 bg-border rounded animate-pulse"></div>
            <div className="h-4 bg-border rounded w-5/6 animate-pulse"></div>
          </div>
          <div className="space-y-2 pt-4">
            <div className="h-4 bg-border rounded animate-pulse"></div>
            <div className="h-4 bg-border rounded animate-pulse"></div>
            <div className="h-4 bg-border rounded w-5/6 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Skeleton for skills section */}
      <div className="card p-6">
        <div className="space-y-3">
          <div className="h-5 bg-border rounded w-24 animate-pulse"></div>
          <div className="flex gap-2">
            <div className="h-8 bg-border rounded-full w-20 animate-pulse"></div>
            <div className="h-8 bg-border rounded-full w-24 animate-pulse"></div>
            <div className="h-8 bg-border rounded-full w-18 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Skeleton for button */}
      <div className="h-12 bg-border rounded animate-pulse"></div>
    </div>
  )
}
