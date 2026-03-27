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
  'JavaScript', 'Python', 'React', 'TypeScript', 'Node.js', 'SQL', 'AWS', 'Docker',
  'Kubernetes', 'Java', 'Go', 'Rust', 'Vue.js', 'Angular', 'C++', 'C#'
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
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Filters Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="text-xs text-blue-600 hover:text-blue-700 font-medium disabled:text-gray-400"
            disabled={isLoading}
          >
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Location Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Location</label>
          <input
            type="text"
            placeholder="e.g., San Francisco"
            value={location}
            onChange={handleLocationChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>

        {/* Experience Level Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Experience Level</label>
          <select
            value={experienceLevel}
            onChange={handleExperienceLevelChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
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
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={isRemote}
              onChange={handleRemoteToggle}
              disabled={isLoading}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:bg-gray-100"
            />
            <span className="ml-2 text-sm text-gray-700">Remote work</span>
          </label>
        </div>

        {/* Skills Filter */}
        <div className="relative" ref={skillsDropdownRef}>
          <label className="block text-xs font-medium text-gray-700 mb-1">Skills</label>
          <button
            type="button"
            onClick={() => setShowSkillsDropdown(!showSkillsDropdown)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-left bg-white hover:bg-gray-50 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <div className="flex items-center justify-between">
              <span className={selectedSkills.length > 0 ? 'text-gray-900' : 'text-gray-500'}>
                {selectedSkills.length > 0 ? `${selectedSkills.length} selected` : 'Select skills'}
              </span>
              <svg className={`w-4 h-4 text-gray-400 transition-transform ${showSkillsDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </button>

          {showSkillsDropdown && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-20 max-h-48 overflow-y-auto">
              {COMMON_SKILLS.map((skill) => (
                <label
                  key={skill}
                  className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer text-sm"
                >
                  <input
                    type="checkbox"
                    checked={selectedSkills.includes(skill)}
                    onChange={() => handleSkillToggle(skill)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-gray-700">{skill}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {location && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                📍 {location}
                <button
                  onClick={() => handleLocationChange({ target: { value: '' } } as any)}
                  className="ml-1 hover:text-blue-600"
                >
                  ×
                </button>
              </span>
            )}
            {experienceLevel && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                📊 {experienceLevel}
                <button
                  onClick={() => handleExperienceLevelChange({ target: { value: '' } } as any)}
                  className="ml-1 hover:text-blue-600"
                >
                  ×
                </button>
              </span>
            )}
            {isRemote && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                💻 Remote
                <button
                  onClick={() => handleRemoteToggle({ target: { checked: false } } as any)}
                  className="ml-1 hover:text-green-600"
                >
                  ×
                </button>
              </span>
            )}
            {selectedSkills.map((skill) => (
              <span key={skill} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                🛠️ {skill}
                <button
                  onClick={() => handleSkillToggle(skill)}
                  className="ml-1 hover:text-purple-600"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

