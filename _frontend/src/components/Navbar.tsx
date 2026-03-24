import { Link } from 'react-router-dom'

export const Navbar = () => {
  return (
    <nav className="bg-white border-b border-border sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-textPrimary">
              JobSync
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              to="/jobs"
              className="btn-primary"
            >
              All Jobs
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}