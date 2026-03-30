import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import JobsList from './pages/JobsList'
import SavedJobs from './pages/SavedJobs'
import { JobDetail } from './components/JobDetail'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<JobsList />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/saved" element={<SavedJobs />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

