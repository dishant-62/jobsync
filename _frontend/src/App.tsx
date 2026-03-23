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

