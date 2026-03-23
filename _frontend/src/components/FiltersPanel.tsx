import React, { useState, useEffect, useRef } from 'react'

interface FiltersPanelProps {
  onFiltersChange: (filters: {
    location: string
    experience_level: string
    is_remote: boolean
    skills: string[]
  }) => void
  isLoading?: boolean
}

const EXPERIENCE_LEVELS = ['Entry Level', 'Mid Level', 'Senior', 'Lead', 'Executive']
const COMMON_SKILLS = [
  'JavaScript',
  'Python',
  'React',
  'TypeScript',
  'Node.js',
  'SQL',
  'AWS',
  'Docker',
  'Kubernetes',
  'Java',
  'Go',
  'Rust',
  'Vue.js',
  'Angular',
  'C++',
  'C#',
]

export const FiltersPanel: React.FC<FiltersPanelProps> = ({ onFiltersChange, isLoading = false }) => {
  const [location, setLocation] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('')
  const [isRemote, setIsRemote] = useState(false)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [showSkillsDropdown, setShowSkillsDropdown] = useState(false)
  const skillsDropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (skillsDropdownRef.current && !skillsDropdownRef.current.contains(event.target as Node)) {
        setShowSkillsDropdown(false)
      }
    }

    if (showSkillsDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showSkillsDropdown])

  const handleLocationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newLocation = e.target.value
    setLocation(newLocation)
    triggerFiltersChange(newLocation, experienceLevel, isRemote, selectedSkills)
  }

  const handleExperienceLevelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLevel = e.target.value
    setExperienceLevel(newLevel)
    triggerFiltersChange(location, newLevel, isRemote, selectedSkills)
  }

  const handleRemoteToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newRemote = e.target.checked
    setIsRemote(newRemote)
    triggerFiltersChange(location, experienceLevel, newRemote, selectedSkills)
  }

  const handleSkillToggle = (skill: string) => {
    const newSkills = selectedSkills.includes(skill)
      ? selectedSkills.filter((s) => s !== skill)
      : [...selectedSkills, skill]
    setSelectedSkills(newSkills)
    triggerFiltersChange(location, experienceLevel, isRemote, newSkills)
  }

  const handleClearFilters = () => {
    setLocation('')
    setExperienceLevel('')
    setIsRemote(false)
    setSelectedSkills([])
    setShowSkillsDropdown(false)
    triggerFiltersChange('', '', false, [])
  }

  const triggerFiltersChange = (
    loc: string,
    exp: string,
    remote: boolean,
    skills: string[]
  ) => {
    onFiltersChange({
      location: loc,
      experience_level: exp,
      is_remote: remote,
      skills,
    })
  }

  const hasActiveFilters = location || experienceLevel || isRemote || selectedSkills.length > 0

  return (
    <div className="mb-6 bg-white p-6 rounded-lg shadow">
      {/* Filters Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">🔽 Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium disabled:text-gray-400"
            disabled={isLoading}
          >
            Clear All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Location Filter */}
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
            📍 Location
          </label>
          <input
            id="location"
            type="text"
            placeholder="e.g., San Francisco"
            value={location}
            onChange={handleLocationChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 transition"
          />
        </div>

        {/* Experience Level Filter */}
        <div>
          <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
            📊 Experience Level
          </label>
          <select
            id="experience"
            value={experienceLevel}
            onChange={handleExperienceLevelChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 transition"
          >
            <option value="">All Levels</option>
            {EXPERIENCE_LEVELS.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </div>

        {/* Remote Checkbox */}
        <div className="flex items-end pb-2">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={isRemote}
              onChange={handleRemoteToggle}
              disabled={isLoading}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 cursor-pointer"
            />
            <span className="ml-2 text-sm font-medium text-gray-700">💻 Remote Only</span>
          </label>
        </div>

        {/* Skills Filter - Dropdown */}
        <div className="relative" ref={skillsDropdownRef}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            🛠️ Skills <span className="text-xs text-gray-400">(coming soon)</span>
          </label>
          <button
            type="button"
            onClick={() => setShowSkillsDropdown(!showSkillsDropdown)}
            disabled={true}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-left bg-gray-100 hover:bg-gray-100 disabled:bg-gray-100 transition cursor-not-allowed"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">
                {selectedSkills.length > 0 ? `${selectedSkills.length} selected` : 'Skills filtering coming soon...'}
              </span>
              <span className={`text-xs transition-transform ${showSkillsDropdown ? 'rotate-180' : ''}`}>▼</span>
            </div>
          </button>

          {showSkillsDropdown && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-20 max-h-64 overflow-y-auto">
              {COMMON_SKILLS.map((skill) => (
                <label
                  key={skill}
                  className="flex items-center px-4 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                >
                  <input
                    type="checkbox"
                    checked={selectedSkills.includes(skill)}
                    onChange={() => handleSkillToggle(skill)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
                  />
                  <span className="ml-2 text-sm text-gray-700">{skill}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

