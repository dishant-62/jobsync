import { useState } from 'react'
import type { ResumeListItem } from '../../types/resume'

interface Props {
  resume: ResumeListItem
  onSelect: (id: string) => void
  onDelete: (id: string) => void
  onSetPrimary: (id: string) => void
}

const SCORE_COLOR: Record<string, string> = {
  A: 'text-emerald-600 bg-emerald-50',
  B: 'text-blue-600 bg-blue-50',
  C: 'text-amber-600 bg-amber-50',
  D: 'text-orange-600 bg-orange-50',
  F: 'text-red-600 bg-red-50',
}

const STATUS_BADGE: Record<string, { label: string; cls: string }> = {
  complete: { label: 'Analysed', cls: 'bg-emerald-50 text-emerald-700' },
  analyzing: { label: 'Analysing…', cls: 'bg-blue-50 text-blue-700 animate-pulse' },
  pending: { label: 'Not analysed', cls: 'bg-gray-100 text-gray-500' },
  error: { label: 'Error', cls: 'bg-red-50 text-red-600' },
}

export function ResumeCard({ resume, onSelect, onDelete, onSetPrimary }: Props) {
  const [menuOpen, setMenuOpen] = useState(false)

  const badge = STATUS_BADGE[resume.analysis_status] ?? STATUS_BADGE.pending
  const scoreColor = resume.score ? SCORE_COLOR[resume.score] : null

  return (
    <tr
      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
      onClick={() => onSelect(resume._id)}
    >
      {/* Name / Primary badge */}
      <td className="py-3 px-4">
        <div className="flex items-center gap-2">
          <span className="text-base font-medium text-gray-900 truncate max-w-[220px]">
            {resume.title}
          </span>
          {resume.is_primary && (
            <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded bg-black text-white">
              Primary
            </span>
          )}
        </div>
        {resume.target_job_title && (
          <p className="text-xs text-gray-400 mt-0.5">{resume.target_job_title}</p>
        )}
      </td>

      {/* Analysis status */}
      <td className="py-3 px-4 hidden sm:table-cell">
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${badge.cls}`}>
          {badge.label}
        </span>
      </td>

      {/* Score */}
      <td className="py-3 px-4 hidden md:table-cell">
        {scoreColor ? (
          <span className={`font-bold text-sm px-2 py-1 rounded ${scoreColor}`}>
            {resume.score}
          </span>
        ) : (
          <span className="text-gray-300 text-sm">—</span>
        )}
      </td>

      {/* Last modified */}
      <td className="py-3 px-4 hidden lg:table-cell text-sm text-gray-400">
        {new Date(resume.updated_at).toLocaleDateString()}
      </td>

      {/* Actions */}
      <td
        className="py-3 px-4 text-right"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative inline-block">
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="p-1.5 rounded-full hover:bg-gray-200 text-gray-400 hover:text-gray-700 transition-colors"
            aria-label="More options"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <circle cx="10" cy="4" r="1.5" />
              <circle cx="10" cy="10" r="1.5" />
              <circle cx="10" cy="16" r="1.5" />
            </svg>
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 z-20 mt-1 w-40 rounded-xl shadow-lg bg-white border border-gray-100 py-1">
                {!resume.is_primary && (
                  <button
                    onClick={() => { onSetPrimary(resume._id); setMenuOpen(false) }}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 text-gray-700"
                  >
                    Set as primary
                  </button>
                )}
                <button
                  onClick={() => { onSelect(resume._id); setMenuOpen(false) }}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 text-gray-700"
                >
                  View / Edit
                </button>
                <button
                  onClick={() => { onDelete(resume._id); setMenuOpen(false) }}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-red-50 text-red-600"
                >
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </td>
    </tr>
  )
}
