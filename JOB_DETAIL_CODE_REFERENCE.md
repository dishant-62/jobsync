# 📚 Job Detail Page - Component Code Reference

Complete source code for all job detail page components.

---

## 1️⃣ App.tsx - Router Setup

**Purpose:** Main application entry point with routing

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import JobsList from './pages/JobsList'
import { JobDetail } from './components/JobDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<JobsList />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

**Key Points:**
- ✅ BrowserRouter wraps all routes
- ✅ Two routes: list (/) and detail (/jobs/:id)
- ✅ Clean, simple setup

---

## 2️⃣ pages/JobsList.tsx - List Page

**Purpose:** Job listing page with search, filters, and pagination

```typescript
import { useState, useEffect, useCallback } from 'react'
import { SearchBar } from '../components/SearchBar'
import { FiltersPanel } from '../components/FiltersPanel'
import { JobList } from '../components/JobList'
import { Pagination } from '../components/Pagination'
import { jobApi } from '../api/client'
import type { Job } from '../types'

function JobsList() {
  // State declarations...
  const [jobs, setJobs] = useState<Job[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('')
  const [isRemote, setIsRemote] = useState(false)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [limit] = useState(20)
  const [offset, setOffset] = useState(0)

  // Fetch logic
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
        limit,
        offset,
      })
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
  }, [searchQuery, location, experienceLevel, isRemote, selectedSkills, limit, offset])

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    setOffset(0)
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
    setOffset(0)
  }

  const handlePageChange = (newOffset: number) => {
    setOffset(newOffset)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">💼 JobSync</h1>
          <p className="text-gray-600 mt-1">Discover your next opportunity</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        <FiltersPanel onFiltersChange={handleFiltersChange} isLoading={isLoading} />
        {total > 0 && (
          <div className="mb-4 text-sm text-gray-600">
            Found <span className="font-semibold">{total}</span> job(s)
          </div>
        )}
        <JobList jobs={jobs} isLoading={isLoading} error={error} />
        <Pagination
          total={total}
          limit={limit}
          offset={offset}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            © 2026 JobSync. Powered by the JobSync Platform API.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default JobsList
```

---

## 3️⃣ components/JobDetail.tsx - Detail Page (NEW)

**Purpose:** Display full job information

```typescript
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { jobApi } from '../api/client'
import type { Job } from '../types'
import { SkeletonLoader } from './SkeletonLoader'

export const JobDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [job, setJob] = useState<Job | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchJobDetail = async () => {
      if (!id) {
        setError('Job ID not provided')
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setError(null)
        const response = await jobApi.getJob(id)
        setJob(response)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch job details'
        setError(errorMessage)
        setJob(null)
      } finally {
        setIsLoading(false)
      }
    }

    fetchJobDetail()
  }, [id])

  const handleBack = () => {
    navigate(-1)
  }

  const formatSalary = (min: number | null | undefined, max: number | null | undefined) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const postedDate = job
    ? new Date(job.posted_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : ''

  const salaryRange = job ? formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined) : null

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">💼 JobSync</h1>
            <p className="text-gray-600 mt-1">View job details</p>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <button
          onClick={handleBack}
          className="mb-6 flex items-center text-blue-600 hover:text-blue-800 font-medium transition"
        >
          <span className="text-xl mr-2">←</span>
          Back to Jobs
        </button>

        {isLoading && <SkeletonLoader />}

        {error && !isLoading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 font-medium">Error loading job details</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
            <button
              onClick={handleBack}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
            >
              Go Back
            </button>
          </div>
        )}

        {job && !isLoading && (
          <div className="space-y-6">
            {/* Header Section */}
            <div className="bg-white rounded-lg shadow p-8">
              <div className="mb-6">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">{job.title}</h1>
                <p className="text-xl text-blue-600 font-semibold">{job.company.name}</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-6 border-t border-gray-200">
                <div>
                  <p className="text-gray-600 text-sm font-medium mb-1">📍 Location</p>
                  <p className="text-gray-900 font-semibold">{job.location}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm font-medium mb-1">💻 Work Mode</p>
                  <p className="text-gray-900 font-semibold">
                    {job.is_remote ? 'Remote' : 'On-site'}
                  </p>
                </div>
                {job.experience_level && (
                  <div>
                    <p className="text-gray-600 text-sm font-medium mb-1">📊 Experience</p>
                    <p className="text-gray-900 font-semibold capitalize">{job.experience_level}</p>
                  </div>
                )}
                {salaryRange && (
                  <div>
                    <p className="text-gray-600 text-sm font-medium mb-1">💰 Salary</p>
                    <p className="text-gray-900 font-semibold">{salaryRange}</p>
                  </div>
                )}
                {!salaryRange && (
                  <div>
                    <p className="text-gray-600 text-sm font-medium mb-1">📅 Posted</p>
                    <p className="text-gray-900 font-semibold">{postedDate}</p>
                  </div>
                )}
              </div>

              {salaryRange && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <p className="text-gray-600 text-sm font-medium mb-1">📅 Posted</p>
                  <p className="text-gray-900 font-semibold">{postedDate}</p>
                </div>
              )}
            </div>

            {/* Description Section */}
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Job Description</h2>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {job.description}
                </p>
              </div>
            </div>

            {/* Skills Section */}
            {job.skills && job.skills.length > 0 && (
              <div className="bg-white rounded-lg shadow p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Required Skills</h2>
                <div className="flex flex-wrap gap-3">
                  {job.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-blue-100 text-blue-800 font-medium text-sm rounded-full hover:bg-blue-200 transition"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Apply Section */}
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Apply?</h2>
              <p className="text-gray-700 mb-6">
                Click the button below to visit the company's application page.
              </p>
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block px-8 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition shadow-md"
              >
                🚀 Apply Now
              </a>
              <p className="text-gray-500 text-sm mt-4">
                You'll be redirected to the company's careers page
              </p>
            </div>

            {/* Additional Information */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-sm text-gray-700">
              <p>
                <strong>Need help?</strong> Visit our{' '}
                <a href="/" className="text-blue-600 hover:text-blue-800">
                  job listings
                </a>{' '}
                to find more opportunities or use our search and filters to narrow down your options.
              </p>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-gray-600 text-sm">
          <p>&copy; 2026 JobSync. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
```

---

## 4️⃣ components/SkeletonLoader.tsx - Loading State (NEW)

**Purpose:** Animated placeholder while loading

```typescript
export const SkeletonLoader = () => {
  return (
    <div className="space-y-4">
      {/* Header skeleton */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-3">
          <div className="h-8 bg-gray-200 rounded w-3/4 animate-pulse"></div>
          <div className="h-5 bg-gray-200 rounded w-1/3 animate-pulse"></div>
          <div className="flex gap-3 pt-2">
            <div className="h-4 bg-gray-200 rounded w-24 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-28 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Description skeleton */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4 animate-pulse"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse"></div>
          </div>
          <div className="space-y-2 pt-4">
            <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Skills skeleton */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-3">
          <div className="h-5 bg-gray-200 rounded w-24 animate-pulse"></div>
          <div className="flex gap-2">
            <div className="h-8 bg-gray-200 rounded-full w-20 animate-pulse"></div>
            <div className="h-8 bg-gray-200 rounded-full w-24 animate-pulse"></div>
            <div className="h-8 bg-gray-200 rounded-full w-18 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Button skeleton */}
      <div className="h-12 bg-gray-200 rounded animate-pulse"></div>
    </div>
  )
}
```

---

## 5️⃣ components/JobCard.tsx - Updated (MODIFIED)

**Key Changes:**
- Added `Link` import from react-router-dom
- Made card header clickable
- Added "View Details" button alongside "Apply Now"

```typescript
import { Link } from 'react-router-dom'
import type { Job } from '../types'

export const JobCard = ({ job }: { job: Job }) => {
  const postedDate = new Date(job.posted_date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  const truncateDescription = (text: string, length: number = 200) => {
    return text.length > length ? text.substring(0, length) + '...' : text
  }

  const formatSalary = (min: number | null | undefined, max: number | null | undefined) => {
    if (!min && !max) return null
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `$${min.toLocaleString()}+`
    return `Up to $${max?.toLocaleString()}`
  }

  const salaryRange = formatSalary(job.salary_min ?? undefined, job.salary_max ?? undefined)

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer">
      <Link to={`/jobs/${job.id}`} className="block hover:opacity-90 transition">
        <div className="mb-3">
          <h3 className="text-xl font-semibold text-gray-900 mb-1 hover:text-blue-600 transition">
            {job.title}
          </h3>
          <p className="text-base text-blue-600 font-medium">{job.company.name}</p>
        </div>

        <div className="flex flex-wrap gap-3 mb-4 text-sm text-gray-600">
          <span>📍 {job.location}</span>
          {job.is_remote && <span>💻 Remote</span>}
          {job.experience_level && <span>📊 {job.experience_level}</span>}
          {salaryRange && <span>💰 {salaryRange}</span>}
        </div>

        <p className="text-gray-700 text-sm mb-4">
          {truncateDescription(job.description)}
        </p>
      </Link>

      {job.skills && job.skills.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-700 mb-2">Required Skills:</p>
          <div className="flex flex-wrap gap-2">
            {job.skills.slice(0, 5).map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 5 && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                +{job.skills.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">Posted: {postedDate}</span>
        <div className="flex gap-2">
          <Link
            to={`/jobs/${job.id}`}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition"
          >
            View Details
          </Link>
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition"
          >
            Apply Now
          </a>
        </div>
      </div>
    </div>
  )
}
```

---

## 📋 API Client (Already Present)

**File:** `src/api/client.ts`

The API client already had the `getJob` method:

```typescript
export const jobApi = {
  listJobs: async (filters: SearchFilters = {}): Promise<JobListResponse> => {
    // ... existing code
  },

  getJob: async (jobId: string) => {
    const response = await client.get(`/jobs/${jobId}`)
    return response.data
  },
}
```

---

## ✅ Summary

**All components are now in place and ready for use:**
1. ✅ Router setup in App.tsx
2. ✅ List page extracted to pages/JobsList.tsx
3. ✅ Detail page created in components/JobDetail.tsx
4. ✅ Skeleton loader for better UX
5. ✅ JobCard updated to be clickable
6. ✅ API client has getJob method
7. ✅ TypeScript types all correct
8. ✅ No compilation errors
9. ✅ Builds successfully

**The implementation is complete and ready for testing!**
