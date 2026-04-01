import type { ResumeSuggestion } from '../../types/resume'

interface Props {
  suggestions: ResumeSuggestion[]
}

const TYPE_STYLES = {
  urgent: {
    dot: 'bg-red-500',
    badge: 'bg-red-50 text-red-700 border-red-200',
    label: 'Urgent',
    border: 'border-l-red-400',
  },
  critical: {
    dot: 'bg-amber-500',
    badge: 'bg-amber-50 text-amber-700 border-amber-200',
    label: 'Critical',
    border: 'border-l-amber-400',
  },
  optional: {
    dot: 'bg-blue-400',
    badge: 'bg-blue-50 text-blue-700 border-blue-200',
    label: 'Optional',
    border: 'border-l-blue-300',
  },
}

export function AISuggestionsPanel({ suggestions }: Props) {
  if (!suggestions.length) {
    return (
      <div className="text-center py-10 text-gray-400 text-sm">
        No suggestions yet — run the analyser to get AI feedback.
      </div>
    )
  }

  // Group by section
  const grouped = suggestions.reduce<Record<string, ResumeSuggestion[]>>((acc, s) => {
    const key = s.section || 'General'
    ;(acc[key] = acc[key] || []).push(s)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([section, items]) => (
        <div key={section}>
          <h4 className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
            {section}
          </h4>
          <div className="space-y-3">
            {items.map((s, idx) => {
              const style = TYPE_STYLES[s.type]
              return (
                <div
                  key={idx}
                  className={`rounded-xl border border-gray-100 border-l-4 ${style.border} bg-white p-4 shadow-sm`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`w-2 h-2 rounded-full ${style.dot} shrink-0`} />
                        <span
                          className={`text-[10px] font-semibold uppercase tracking-wide border rounded px-1.5 py-0.5 ${style.badge}`}
                        >
                          {style.label}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800 font-medium">{s.issue}</p>
                      {s.suggestion && (
                        <p className="text-sm text-gray-600 mt-0.5">{s.suggestion}</p>
                      )}
                      {s.improved_text && (
                        <div className="mt-2 rounded-lg bg-gray-50 border border-dashed border-gray-200 px-3 py-2">
                          <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1">
                            Suggested
                          </p>
                          <p className="text-sm text-gray-700 italic">{s.improved_text}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
