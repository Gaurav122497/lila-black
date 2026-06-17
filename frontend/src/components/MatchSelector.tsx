import { useStore } from '../store'
import { useMatches } from '../api'

export default function MatchSelector() {
  const { selectedMap, selectedDates, selectedMatch, setSelectedMatch } = useStore()
  const { data, isLoading } = useMatches(selectedMap, selectedDates)

  const matches = data?.matches ?? []

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-border">
        <span className="text-xs text-slate-500">
          {isLoading ? 'Loading…' : `${matches.length} matches`}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {matches.map((m) => (
          <button
            key={m.match_id}
            onClick={() => setSelectedMatch(m.match_id)}
            className={`w-full text-left px-3 py-2 border-b border-border transition-colors ${
              selectedMatch === m.match_id
                ? 'bg-accent/20 border-l-2 border-l-accent'
                : 'hover:bg-border'
            }`}
          >
            <div className="text-xs text-slate-300 truncate font-mono">
              {m.match_id.slice(0, 16)}…
            </div>
            <div className="flex gap-3 mt-0.5 text-[10px] text-slate-500">
              <span>{m.date.replace('_', ' ')}</span>
              <span className="text-blue-400">👤{m.human_count}</span>
              <span className="text-slate-600">🤖{m.bot_count}</span>
              <span className="text-red-400">⚔{m.kill_count}</span>
            </div>
          </button>
        ))}
        {!isLoading && matches.length === 0 && (
          <div className="p-4 text-xs text-slate-600 text-center">
            No matches for selected filters
          </div>
        )}
      </div>
    </div>
  )
}
