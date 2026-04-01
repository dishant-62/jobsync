import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'

// ── Types ─────────────────────────────────────────────────────────────────

export interface AuthUser {
  _id: string
  name: string
  email: string
  provider: 'google' | 'linkedin' | 'local'
  profile_pic: string | null
  created_at: string
}

interface AuthContextValue {
  user: AuthUser | null
  /** True only during the initial session-restore fetch on mount */
  isInitialising: boolean
  /** True while a login / register request is in-flight */
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  /** Manually set a user (used by AuthCallback after an OAuth redirect) */
  setUser: (user: AuthUser | null) => void
  clearError: () => void
}

// ── Context ───────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null)

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}

// ── Auth server base URL ──────────────────────────────────────────────────
// In development this is the direct Node auth server.
// In production, point VITE_AUTH_URL to your deployed auth service.
const AUTH_BASE = (import.meta.env.VITE_AUTH_URL as string) || 'http://localhost:4000'

async function authFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${AUTH_BASE}${path}`, {
    ...init,
    credentials: 'include', // send / receive HTTP-only cookies
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })

  // Try to parse JSON; fall back to empty object if body is empty
  const data: Record<string, unknown> = await res.json().catch(() => ({}))

  if (!res.ok) {
    throw new Error((data.error as string) || 'Request failed')
  }

  return data
}

// ── Provider ──────────────────────────────────────────────────────────────

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isInitialising, setIsInitialising] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Restore session from existing JWT cookie on first render
  useEffect(() => {
    authFetch('/auth/me')
      .then((data) => setUser(data.user as AuthUser))
      .catch(() => setUser(null))
      .finally(() => setIsInitialising(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setError(null)
    setIsLoading(true)
    try {
      const data = await authFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setUser(data.user as AuthUser)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed'
      setError(msg)
      throw new Error(msg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(async (name: string, email: string, password: string) => {
    setError(null)
    setIsLoading(true)
    try {
      const data = await authFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password }),
      })
      setUser(data.user as AuthUser)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed'
      setError(msg)
      throw new Error(msg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    await authFetch('/auth/logout', { method: 'POST' }).catch(() => {})
    setUser(null)
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return (
    <AuthContext.Provider
      value={{ user, isInitialising, isLoading, error, login, register, logout, setUser, clearError }}
    >
      {children}
    </AuthContext.Provider>
  )
}
