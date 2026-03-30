import React, { useEffect, useRef, useState } from 'react'
import { Button } from './ui/Button'
import { useAuth } from '../context/AuthContext'

// ── Auth server base URL ──────────────────────────────────────────────────
const AUTH_BASE = (import.meta.env.VITE_AUTH_URL as string) || 'http://localhost:4000'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

type Mode = 'signin' | 'register'

const Spinner: React.FC = () => (
  <span
    className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
    aria-hidden="true"
  />
)

const GoogleIcon: React.FC = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
    <path
      d="M17.64 9.205c0-.639-.057-1.252-.164-1.841H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"
      fill="#4285F4"
    />
    <path
      d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"
      fill="#34A853"
    />
    <path
      d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"
      fill="#FBBC05"
    />
    <path
      d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z"
      fill="#EA4335"
    />
  </svg>
)

const LinkedInIcon: React.FC = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="#0A66C2" aria-hidden="true">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
  </svg>
)

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const overlayRef = useRef<HTMLDivElement>(null)
  const { login, register, isLoading, error, clearError, user } = useAuth()

  const [mode, setMode] = useState<Mode>('signin')
  const [showEmailForm, setShowEmailForm] = useState(false)
  const [oauthLoading, setOauthLoading] = useState<'google' | 'linkedin' | null>(null)

  // Form fields
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)

  // Close when auth succeeds
  useEffect(() => {
    if (user && isOpen) onClose()
  }, [user, isOpen, onClose])

  // Keyboard + scroll lock
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    if (isOpen) {
      document.addEventListener('keydown', onKey)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [isOpen, onClose])

  // Reset when modal reopens
  useEffect(() => {
    if (isOpen) {
      setMode('signin')
      setShowEmailForm(false)
      setName('')
      setEmail('')
      setPassword('')
      setLocalError(null)
      clearError()
    }
  }, [isOpen, clearError])

  if (!isOpen) return null

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === overlayRef.current) onClose()
  }

  // Navigate browser directly to auth server for OAuth
  const handleOAuth = (provider: 'google' | 'linkedin') => {
    setOauthLoading(provider)
    window.location.href = `${AUTH_BASE}/auth/${provider}`
  }

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)
    try {
      if (mode === 'register') {
        await register(name.trim(), email, password)
      } else {
        await login(email, password)
      }
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  const displayError = localError || error

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4"
      role="dialog"
      aria-modal="true"
      aria-label="Sign in"
    >
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 animate-modal-in">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          aria-label="Close modal"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M12.854 3.146a.5.5 0 0 0-.708 0L8 7.293 3.854 3.146a.5.5 0 1 0-.708.708L7.293 8l-4.147 4.146a.5.5 0 0 0 .708.708L8 8.707l4.146 4.147a.5.5 0 0 0 .708-.708L8.707 8l4.147-4.146a.5.5 0 0 0 0-.708z" />
          </svg>
        </button>

        {/* Header */}
        <div className="mb-7 text-center">
          <div className="inline-flex items-center gap-2 mb-4">
            <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-gray-900">
              <svg width="18" height="18" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <path d="M6 16a10 10 0 0 1 20 0" stroke="white" strokeWidth="3" strokeLinecap="round" fill="none" />
                <circle cx="16" cy="16" r="3.5" fill="white" />
                <path d="M19.5 16l3.5-3.5M12.5 16l-3.5-3.5" stroke="white" strokeWidth="2.2" strokeLinecap="round" fill="none" />
              </svg>
            </span>
            <span className="text-xl font-bold text-gray-900">JobSync</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            {mode === 'signin' ? 'Welcome back' : 'Create account'}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            {mode === 'signin'
              ? 'Sign in to access your personalised job feed'
              : 'Join thousands of job seekers on JobSync'}
          </p>
        </div>

        {/* Error banner */}
        {displayError && (
          <div className="mb-4 flex items-start gap-2 rounded-xl bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-700 animate-dropdown-in">
            <svg className="mt-0.5 shrink-0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {displayError}
          </div>
        )}

        {/* OAuth buttons */}
        <div className="space-y-3">
          <button
            type="button"
            disabled={oauthLoading !== null || isLoading}
            onClick={() => handleOAuth('google')}
            className="flex w-full items-center justify-center gap-3 rounded-full border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 hover:border-gray-300 transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {oauthLoading === 'google' ? <Spinner /> : <GoogleIcon />}
            {oauthLoading === 'google' ? 'Redirecting…' : 'Continue with Google'}
          </button>

          <button
            type="button"
            disabled={oauthLoading !== null || isLoading}
            onClick={() => handleOAuth('linkedin')}
            className="flex w-full items-center justify-center gap-3 rounded-full border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 hover:border-gray-300 transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {oauthLoading === 'linkedin' ? <Spinner /> : <LinkedInIcon />}
            {oauthLoading === 'linkedin' ? 'Redirecting…' : 'Continue with LinkedIn'}
          </button>
        </div>

        {/* Divider */}
        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-gray-200" />
          <span className="text-xs text-gray-400 font-medium">or</span>
          <div className="h-px flex-1 bg-gray-200" />
        </div>

        {/* Email section */}
        {!showEmailForm ? (
          <button
            type="button"
            disabled={oauthLoading !== null}
            onClick={() => setShowEmailForm(true)}
            className="flex w-full items-center justify-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 hover:border-gray-300 transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
            </svg>
            Continue with Email
          </button>
        ) : (
          <form onSubmit={handleEmailSubmit} className="space-y-3 animate-dropdown-in" noValidate>
            {mode === 'register' && (
              <input
                type="text"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoComplete="name"
                className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-900/10 transition-all"
              />
            )}
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-900/10 transition-all"
            />
            <input
              type="password"
              placeholder={mode === 'register' ? 'Password (min 8 chars)' : 'Password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
              className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 placeholder-gray-400 outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-900/10 transition-all"
            />
            <Button variant="primary" size="lg" fullWidth type="submit" disabled={isLoading}>
              {isLoading
                ? <><Spinner />{mode === 'register' ? 'Creating account…' : 'Signing in…'}</>
                : mode === 'register' ? 'Create account' : 'Sign In'}
            </Button>
            <p className="text-center text-xs text-gray-500 pt-1">
              {mode === 'signin' ? (
                <>Don&apos;t have an account?{' '}
                  <button type="button" onClick={() => { setMode('register'); setLocalError(null); clearError() }} className="font-semibold text-gray-900 hover:underline">Sign up</button>
                </>
              ) : (
                <>Already have an account?{' '}
                  <button type="button" onClick={() => { setMode('signin'); setLocalError(null); clearError() }} className="font-semibold text-gray-900 hover:underline">Sign in</button>
                </>
              )}
            </p>
            <button type="button" onClick={() => { setShowEmailForm(false); setLocalError(null); clearError() }} className="w-full text-center text-xs text-gray-400 hover:text-gray-600 transition-colors">
              ← Back to all options
            </button>
          </form>
        )}

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-gray-400">
          By continuing you agree to our{' '}
          <a href="/terms" className="underline hover:text-gray-700 transition-colors">Terms</a>{' '}
          and{' '}
          <a href="/privacy" className="underline hover:text-gray-700 transition-colors">Privacy Policy</a>
        </p>
      </div>
    </div>
  )
}
