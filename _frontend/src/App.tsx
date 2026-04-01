import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import JobsList from './pages/JobsList'
import SavedJobs from './pages/SavedJobs'
import AuthCallback from './pages/AuthCallback'
import ResumeDashboard from './pages/ResumeDashboard'
import ResumeDetail from './pages/ResumeDetail'
import { JobDetail } from './components/JobDetail'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/jobs" element={<JobsList />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
          <Route path="/saved" element={<SavedJobs />} />
          <Route path="/resume" element={<ResumeDashboard />} />
          <Route path="/resume/:id" element={<ResumeDetail />} />
          {/* OAuth redirect landing — auth server sends users here */}
          <Route path="/auth/callback" element={<AuthCallback />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

