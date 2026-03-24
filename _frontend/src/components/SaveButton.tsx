import React, { useState, useEffect } from 'react'
import { jobApi } from '../api/client'

interface SaveButtonProps {
  jobId: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const SaveButton: React.FC<SaveButtonProps> = ({
  jobId,
  size = 'md',
  className = ''
}) => {
  const [isSaved, setIsSaved] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isChecking, setIsChecking] = useState(true)

  // Check if job is saved on mount
  useEffect(() => {
    const checkSavedStatus = async () => {
      try {
        const saved = await jobApi.isJobSaved(jobId)
        setIsSaved(saved)
      } catch (error) {
        console.error('Failed to check saved status:', error)
      } finally {
        setIsChecking(false)
      }
    }

    checkSavedStatus()
  }, [jobId])

  const handleToggleSave = async () => {
    if (isLoading) return

    setIsLoading(true)
    try {
      if (isSaved) {
        await jobApi.unsaveJob(jobId)
        setIsSaved(false)
        // Show toast notification
        showToast('Job removed from saved jobs', 'success')
      } else {
        await jobApi.saveJob(jobId)
        setIsSaved(true)
        // Show toast notification
        showToast('Job saved successfully!', 'success')
      }
    } catch (error: any) {
      console.error('Failed to toggle save:', error)
      const message = error.response?.data?.detail || 'Failed to save job'
      showToast(message, 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const showToast = (message: string, type: 'success' | 'error') => {
    // Simple toast implementation - in a real app you'd use a proper toast library
    const toast = document.createElement('div')
    toast.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-lg text-white text-sm font-medium ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`
    toast.textContent = message
    document.body.appendChild(toast)

    setTimeout(() => {
      toast.remove()
    }, 3000)
  }

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  }

  const iconSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl'
  }

  if (isChecking) {
    return (
      <button
        className={`flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 transition-colors ${sizeClasses[size]} ${className}`}
        disabled
      >
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
      </button>
    )
  }

  return (
    <button
      onClick={handleToggleSave}
      disabled={isLoading}
      className={`flex items-center justify-center rounded-full transition-colors ${
        isSaved
          ? 'bg-yellow-100 hover:bg-yellow-200 text-yellow-600'
          : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
      } ${sizeClasses[size]} ${className}`}
      title={isSaved ? 'Remove from saved jobs' : 'Save job'}
    >
      {isLoading ? (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
      ) : (
        <span className={iconSizeClasses[size]}>
          {isSaved ? '⭐' : '☆'}
        </span>
      )}
    </button>
  )
}