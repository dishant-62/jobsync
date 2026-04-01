import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Button } from './ui/Button'
import { AuthModal } from './AuthModal'
import { useAuth } from '../context/AuthContext'

// ─── Types ───────────────────────────────────────────────────────────────────

interface NavItem {
  label: string
  href?: string
  dropdown?: DropdownItem[]
}

interface DropdownItem {
  label: string
  description: string
  href: string
  icon: React.ReactNode
}

// ─── Static data ─────────────────────────────────────────────────────────────

const featuresDropdown: DropdownItem[] = [
  {
    label: 'Job Matching',
    description: 'AI-powered matches tailored to your profile',
    href: '/features/matching',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    ),
  },
  {
    label: 'Smart Alerts',
    description: 'Real-time notifications for new openings',
    href: '/features/alerts',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </svg>
    ),
  },
  {
    label: 'Salary Insights',
    description: 'Market data to strengthen your offer',
    href: '/features/salary',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <line x1="12" y1="1" x2="12" y2="23" />
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </svg>
    ),
  },
  {
    label: 'Application Tracker',
    description: 'Keep every application organised in one view',
    href: '/features/tracker',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
]

const mainNavItems: NavItem[] = [
  { label: 'Features', dropdown: featuresDropdown },
  { label: 'AI Agent', href: '/ai-agent' },
  { label: 'Resume AI', href: '/resume' },
  { label: 'For Employers', href: '/employers' },
  { label: 'About Us', href: '/about' },
  { label: 'Blog', href: '/blog' },
]

// ─── Logo ─────────────────────────────────────────────────────────────────────

const Logo: React.FC = () => (
  <Link to="/" className="inline-flex items-center gap-2.5 shrink-0 group" aria-label="JobSync home">
    <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-gray-900 group-hover:bg-gray-700 transition-colors">
      <svg width="18" height="18" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <path d="M6 16a10 10 0 0 1 20 0" stroke="white" strokeWidth="3" strokeLinecap="round" fill="none" />
        <circle cx="16" cy="16" r="3.5" fill="white" />
        <path d="M19.5 16l3.5-3.5M12.5 16l-3.5-3.5" stroke="white" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      </svg>
    </span>
    <span className="text-lg font-bold text-gray-900 tracking-tight leading-none">
      Job<span className="text-gray-500 font-semibold">Sync</span>
    </span>
  </Link>
)

// ─── Features Dropdown ───────────────────────────────────────────────────────

const FeaturesDropdown: React.FC<{ items: DropdownItem[] }> = ({ items }) => (
  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 p-3 z-50 animate-dropdown-in">
    <div className="grid gap-1">
      {items.map((item) => (
        <a
          key={item.label}
          href={item.href}
          className="flex items-start gap-3 rounded-xl px-3 py-2.5 hover:bg-gray-50 transition-colors group"
        >
          <span className="mt-0.5 text-gray-400 group-hover:text-gray-700 transition-colors shrink-0">
            {item.icon}
          </span>
          <div>
            <p className="text-sm font-medium text-gray-900">{item.label}</p>
            <p className="text-xs text-gray-500 mt-0.5 leading-snug">{item.description}</p>
          </div>
        </a>
      ))}
    </div>
  </div>
)

// ─── Desktop Nav Item ────────────────────────────────────────────────────────

const DesktopNavItem: React.FC<{ item: NavItem }> = ({ item }) => {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  const baseClass =
    'text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors duration-150 flex items-center gap-1 py-1'

  if (item.dropdown) {
    return (
      <div ref={ref} className="relative">
        <button
          className={baseClass}
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-haspopup="true"
        >
          {item.label}
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
            aria-hidden="true"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        {open && <FeaturesDropdown items={item.dropdown} />}
      </div>
    )
  }

  return (
    <a href={item.href} className={baseClass}>
      {item.label}
    </a>
  )
}

// ─── Mobile Menu ─────────────────────────────────────────────────────────────

interface MobileMenuProps {
  isOpen: boolean
  onClose: () => void
  onSignIn: () => void
  user: { name: string; email: string; profile_pic: string | null } | null
  onLogout: () => void
}

const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose, onSignIn, user, onLogout }) => {
  const [featuresOpen, setFeaturesOpen] = useState(false)

  // Trap scroll when open
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/30 backdrop-blur-sm transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-in panel */}
      <div
        className={`fixed top-0 right-0 z-50 h-full w-72 max-w-[85vw] bg-white shadow-2xl flex flex-col transition-transform duration-300 ease-out ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
        role="dialog"
        aria-modal="true"
        aria-label="Navigation menu"
      >
        {/* Panel header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <Logo />
          <button
            onClick={onClose}
            className="p-2 rounded-full text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
            aria-label="Close menu"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M12.854 3.146a.5.5 0 0 0-.708 0L8 7.293 3.854 3.146a.5.5 0 1 0-.708.708L7.293 8l-4.147 4.146a.5.5 0 0 0 .708.708L8 8.707l4.146 4.147a.5.5 0 0 0 .708-.708L8.707 8l4.147-4.146a.5.5 0 0 0 0-.708z" />
            </svg>
          </button>
        </div>

        {/* Nav links */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {/* Features with accordion */}
          <div>
            <button
              className="flex w-full items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              onClick={() => setFeaturesOpen((v) => !v)}
              aria-expanded={featuresOpen}
            >
              Features
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                className={`transition-transform duration-200 ${featuresOpen ? 'rotate-180' : ''}`}
                aria-hidden="true"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            {featuresOpen && (
              <div className="mt-1 ml-2 space-y-0.5 animate-dropdown-in">
                {featuresDropdown.map((f) => (
                  <a
                    key={f.label}
                    href={f.href}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                  >
                    <span className="text-gray-400">{f.icon}</span>
                    {f.label}
                  </a>
                ))}
              </div>
            )}
          </div>

          {mainNavItems
            .filter((i) => !i.dropdown)
            .map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="flex items-center px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                onClick={onClose}
              >
                {item.label}
              </a>
            ))}
        </nav>

        {/* CTA */}
        <div className="px-4 py-5 border-t border-gray-100 space-y-2.5">
          {user ? (
            <>
              <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-gray-50 mb-1">
                <span className="flex items-center justify-center w-9 h-9 rounded-full bg-gray-900 text-white text-sm font-bold shrink-0">
                  {user.profile_pic
                    ? <img src={user.profile_pic} alt={user.name} className="w-9 h-9 rounded-full object-cover" />
                    : user.name.charAt(0).toUpperCase()}
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">{user.name}</p>
                  <p className="text-xs text-gray-500 truncate">{user.email}</p>
                </div>
              </div>
              <a href="/saved" className="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors" onClick={onClose}>
                ⭐ Saved Jobs
              </a>
              <Button variant="outline" size="lg" fullWidth onClick={() => { onLogout(); onClose() }}>
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="lg" fullWidth onClick={() => { onClose(); onSignIn() }}>Sign In</Button>
              <Button variant="primary" size="lg" fullWidth>Join Now</Button>
            </>
          )}
        </div>
      </div>
    </>
  )
}

// ─── User Menu (desktop) ─────────────────────────────────────────────────────

interface UserMenuProps {
  user: { name: string; email: string; profile_pic: string | null }
  onLogout: () => void
}

const UserMenu: React.FC<UserMenuProps> = ({ user, onLogout }) => {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  const initials = user.name
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2.5 rounded-full pl-1 pr-3 py-1 hover:bg-gray-100 transition-colors"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-900 text-white text-xs font-bold overflow-hidden">
          {user.profile_pic
            ? <img src={user.profile_pic} alt={user.name} className="w-full h-full object-cover" />
            : initials}
        </span>
        <span className="text-sm font-medium text-gray-900 max-w-[120px] truncate">{user.name.split(' ')[0]}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
          className={`text-gray-400 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} aria-hidden="true">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-2xl shadow-xl border border-gray-100 p-2 z-50 animate-dropdown-in">
          {/* User info */}
          <div className="px-3 py-2.5 border-b border-gray-100 mb-1">
            <p className="text-sm font-semibold text-gray-900 truncate">{user.name}</p>
            <p className="text-xs text-gray-500 truncate">{user.email}</p>
          </div>
          <a href="/saved"
            className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            onClick={() => setOpen(false)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" /></svg>
            Saved Jobs
          </a>
          <div className="border-t border-gray-100 mt-1 pt-1">
            <button
              onClick={() => { onLogout(); setOpen(false) }}
              className="flex w-full items-center gap-2.5 px-3 py-2 rounded-xl text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Navbar ───────────────────────────────────────────────────────────────────

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <>
      <header
        className={[
          'sticky top-0 z-30 w-full bg-white/95 backdrop-blur-md transition-shadow duration-300',
          scrolled ? 'shadow-[0_2px_20px_rgba(0,0,0,0.08)]' : 'border-b border-gray-100',
        ].join(' ')}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between gap-6">

            {/* ── Left: Logo ── */}
            <Logo />

            {/* ── Center: Desktop Nav ── */}
            <nav className="hidden lg:flex items-center gap-6" aria-label="Main navigation">
              {mainNavItems.map((item) => (
                <DesktopNavItem key={item.label} item={item} />
              ))}
            </nav>

            {/* ── Right: User menu OR auth CTAs ── */}
            <div className="hidden lg:flex items-center gap-2 shrink-0">
              {user ? (
                <UserMenu user={user} onLogout={logout} />
              ) : (
                <>
                  <Button variant="ghost" size="md" onClick={() => setAuthOpen(true)}>Sign In</Button>
                  <Button variant="primary" size="md">Join Now</Button>
                </>
              )}
            </div>

            {/* ── Mobile: Hamburger ── */}
            <button
              className="lg:hidden ml-auto p-2 rounded-xl text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              onClick={() => setMobileOpen(true)}
              aria-label="Open menu"
              aria-expanded={mobileOpen}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>

          </div>
        </div>
      </header>

      {/* Mobile slide-in menu */}
      <MobileMenu
        isOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        onSignIn={() => setAuthOpen(true)}
        user={user}
        onLogout={logout}
      />

      {/* Auth modal */}
      <AuthModal isOpen={authOpen} onClose={() => setAuthOpen(false)} />
    </>
  )
}