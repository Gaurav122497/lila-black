import { useState } from 'react'
import { useStore } from '../store'
import { useInsights } from '../api'

const SEVERITY_STYLES = {
  critical: 'border-red-500/50 bg-red-950/20',
  warning:  'border-yellow-500/50 bg-yellow-950/20',
  info:     'border-blue-500/50 bg-blue-950/20',
}

const SEVERITY_ICON = {
  critical: '🔴',
  warning:  '🟡',
  info:     '🔵',
}

export default function InsightsPanel() {
  const { selectedMap } = useStore()
  const { data, isLoading } = useInsights(selectedMap)
  const [expanded, setExpanded] = useState<string | null>(null)

  if (isLoading) {
    return <div className="p-4 text-xs text-slate-600">Computing insights…</div>
  }

  const insights = data?.insights ?? []

  return (
    <div className="p-4 flex flex-col gap-3 overflow-y-auto h-full">
      <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
        Data Insights
      </h2>
      {insights.map((ins) => (
        <button
          key={ins.id}
          onClick={() => setExpanded(expanded === ins.id ? null : ins.id)}
          className={`text-left rounded border p-3 transition-colors ${SEVERITY_STYLES[ins.severity]}`}
        >
          <div className="flex items-start gap-2">
            <span className="text-base leading-none mt-0.5">{SEVERITY_ICON[ins.severity]}</span>
            <div>
              <div className="text-xs font-semibold text-slate-200">{ins.title}</div>
              {expanded === ins.id && (
                <>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{ins.body}</p>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    {ins.stats.map((s) => (
                      <div key={s.label} className="bg-black/30 rounded p-1.5">
                        <div className="text-[9px] text-slate-500">{s.label}</div>
                        <div className="text-xs font-semibold text-slate-200">{s.value}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </button>
      ))}
    </div>
  )
}
