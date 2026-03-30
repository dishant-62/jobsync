import React, { useState, useEffect, useRef } from 'react'

interface FiltersPanelProps {
  onFiltersChange: (filters: {
    location: string
    experience_level: string
    is_remote: boolean
    skills: string[]
  }) => void
  isLoading?: boolean
  isCollapsed?: boolean
  onToggleCollapse?: () => void
}

const EXPERIENCE_LEVELS = ['Entry Level', 'Mid Level', 'Senior', 'Lead', 'Executive']
const COMMON_SKILLS = [
  'JavaScript', 'Python', 'React', 'TypeScript', 'Node.js', 'SQL', 'AWS', 'Docker',
  'Kubernetes', 'Java', 'Go', 'Rust', 'Vue.js', 'Angular', 'C++', 'C#'
]

export const FiltersPanel: React.FC<FiltersPanelProps> = ({
  onFiltersChange,
  isLoading = false,
  isCollapsed = false,
  onToggleCollapse
}) => {
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

  if (isCollapsed) {
    return (
      <div className="w-12 bg-white border-r border-gray-200 flex flex-col items-center py-4">
        <button
          onClick={onToggleCollapse}
          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          title="Show filters"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        </button>
        {hasActiveFilters && (
          <div className="mt-2 w-2 h-2 bg-blue-500 rounded-full"></div>
        )}
      </div>
    )
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
          <button
            onClick={onToggleCollapse}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="Hide filters"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            disabled={isLoading}
            className="w-full mb-6 px-3 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
          >
            Clear all filters
          </button>
        )}

        <div className="space-y-6">
          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-3">Location</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="City, state, or country"
                value={location}
                onChange={handleLocationChange}
                disabled={isLoading}
                className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
              />
            </div>
          </div>

          {/* Experience Level */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-3">Experience Level</label>
            <select
              value={experienceLevel}
              onChange={handleExperienceLevelChange}
              disabled={isLoading}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
            >
              <option value="">All Levels</option>
              {EXPERIENCE_LEVELS.map((level) => (
                <option key={level} value={level}>
                  {level}
                </option>
              ))}
            </select>
          </div>

          {/* Remote Work */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isRemote}
                onChange={handleRemoteToggle}
                disabled={isLoading}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:opacity-50"
              />
              <span className="ml-3 text-sm font-medium text-gray-900">Remote work</span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-7">Include remote positions</p>
          </div>

          {/* Skills */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-3">Skills & Technologies</label>
            <div className="relative" ref={skillsDropdownRef}>
              <button
                type="button"
                onClick={() => setShowSkillsDropdown(!showSkillsDropdown)}
                disabled={isLoading}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-left bg-white hover:bg-gray-50 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              >
                <div className="flex items-center justify-between">
                  <span className={selectedSkills.length > 0 ? 'text-gray-900' : 'text-gray-500'}>
                    {selectedSkills.length > 0
                      ? `${selectedSkills.length} skill${selectedSkills.length !== 1 ? 's' : ''} selected`
                      : 'Select skills'
                    }
                  </span>
                  <svg className={`w-4 h-4 text-gray-400 transition-transform ${showSkillsDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {showSkillsDropdown && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-20 max-h-64 overflow-y-auto">
                  <div className="p-2">
                    {COMMON_SKILLS.map((skill) => (
                      <label
                        key={skill}
                        className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer text-sm rounded-md"
                      >
                        <input
                          type="checkbox"
                          checked={selectedSkills.includes(skill)}
                          onChange={() => handleSkillToggle(skill)}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="ml-3 text-gray-700">{skill}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Selected Skills Tags */}
            {selectedSkills.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {selectedSkills.map((skill) => (
                  <span key={skill} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                    {skill}
                    <button
                      onClick={() => handleSkillToggle(skill)}
                      className="ml-1 hover:text-blue-600"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Active Filters Summary */}
        {hasActiveFilters && (
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Active Filters</h3>
            <div className="space-y-2">
              {location && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">📍 Location</span>
                  <span className="text-gray-900 font-medium">{location}</span>
                </div>
              )}
              {experienceLevel && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">📊 Experience</span>
                  <span className="text-gray-900 font-medium">{experienceLevel}</span>
                </div>
              )}
              {isRemote && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">💻 Remote</span>
                  <span className="text-gray-900 font-medium">Yes</span>
                </div>
              )}
              {selectedSkills.length > 0 && (
                <div className="text-sm">
                  <span className="text-gray-600">🛠️ Skills ({selectedSkills.length})</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

