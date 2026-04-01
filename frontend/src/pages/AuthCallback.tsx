import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth, type AuthUser } from '../context/AuthContext'

const AUTH_BASE = (import.meta.env.VITE_AUTH_URL as string) || 'http://localhost:4000'

/**
 * Landing page after an OAuth redirect.
 * The auth server has already set the JWT cookie; we just call /auth/me to
 * hydrate the context, then send the user to the dashboard.
 */
export default function AuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { setUser } = useAuth()

  useEffect(() => {
    const success = params.get('success')
    const error = params.get('error')

    if (!success || error) {
      // OAuth failed — go home and surface the error in the modal
      navigate(`/?authError=${error ?? 'unknown'}`, { replace: true })
      return
    }

    // Fetch the user that was just authenticated
    fetch(`${AUTH_BASE}/auth/me`, { credentials: 'include' })
      .then((r) => r.json())
      .then((data: { user: AuthUser }) => {
        if (data?.user) setUser(data.user)
        navigate('/', { replace: true })
      })
      .catch(() => {
        navigate('/?authError=session_error', { replace: true })
      })
  }, [navigate, params, setUser])

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-4">
        <div className="w-9 h-9 border-[3px] border-gray-900 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-500 font-medium">Signing you in…</p>
      </div>
    </div>
  )
}
