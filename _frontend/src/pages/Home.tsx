import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { FeaturedJobs } from '../components/FeaturedJobs'
import { jobApi } from '../api/client'
import type { Job } from '../types'

function Home() {
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchFeaturedJobs = async () => {
      try {
        const response = await jobApi.listJobs({ limit: 6 })
        setFeaturedJobs(response.jobs)
      } catch (error) {
        console.error('Failed to fetch featured jobs:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchFeaturedJobs()
  }, [])

  const scrollToFeatured = () => {
    const element = document.getElementById('featured-jobs')
    element?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-textPrimary mb-6">
            Find Your Next{' '}
            <span className="bg-gradient-to-r from-primary to-primaryHover bg-clip-text text-transparent">
              Dream Job
            </span>{' '}
            🚀
          </h1>
          <p className="text-xl text-textSecondary mb-12 max-w-2xl mx-auto">
            Browse thousands of jobs across AI, Software, Cloud, and Data roles.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/jobs"
              className="btn-primary text-lg px-8 py-4"
            >
              Explore Jobs
            </Link>
            <button
              onClick={scrollToFeatured}
              className="bg-white text-textPrimary border-2 border-border rounded-lg px-8 py-4 font-semibold hover:bg-gray-50 transition-colors duration-200"
            >
              View Featured Jobs
            </button>
          </div>
        </div>
      </section>

      {/* Featured Jobs Section */}
      <section id="featured-jobs" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-textPrimary text-center mb-12">
            🔥 Featured Jobs
          </h2>
          <FeaturedJobs jobs={featuredJobs} isLoading={isLoading} />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-primary">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to find your next opportunity?
          </h2>
          <Link
            to="/jobs"
            className="bg-white text-primary font-semibold px-8 py-4 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          >
            Browse All Jobs
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-border py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-textSecondary">
            © 2026 JobSync. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Home