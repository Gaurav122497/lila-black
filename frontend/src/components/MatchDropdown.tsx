import { useState } from 'react'
import { useStore } from '../store'
import { useMaps, useMatches } from '../api'
import { DAYS } from '../constants'

const SELECT_CLS =
  'bg-panel border border-border rounded px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-accent cursor-pointer hover:border-slate-500 transition-colors'

export default function MatchDropdown() {
  const {
    selectedMap, setSelectedMap,
    selectedDates, setSelectedDates,
    selectedMatch, setSelectedMatch,
  } = useStore()

  const [search, setSearch] = useState('')

  const { data: mapsData } = useMaps()
  const maps = mapsData?.maps ?? []

  const activeDate = selectedDates.length === 1 ? selectedDates[0] : ''

  function handleDateChange(val: string) {
    setSelectedDates(val ? [val] : DAYS)
    setSelectedMatch(null)
    setSearch('')
  }

  function handleMapChange(val: string) {
    setSelectedMap(val)
    setSearch('')
  }

  const { data, isLoading } = useMatches(selectedMap, selectedDates)
  const matches = data?.matches ?? []

  const filtered = search.trim()
    ? matches.filter((m) => m.match_id.toLowerCase().includes(search.trim().toLowerCase()))
    : matches

  return (
    <div className="flex items-center gap-2 px-4 h-full">
      {/* Map */}
      <label className="text-[10px] text-slate-500 uppercase tracking-wider shrink-0">Map</label>
      <select
        value={selectedMap}
        onChange={(e) => handleMapChange(e.target.value)}
        className={SELECT_CLS}
      >
        {maps.map((m) => (
          <option key={m.map_id} value={m.map_id}>
            {m.map_id} ({m.total_matches})
          </option>
        ))}
      </select>

      <span className="text-border shrink-0">|</span>

      {/* Date */}
      <label className="text-[10px] text-slate-500 uppercase tracking-wider shrink-0">Date</label>
      <select
        value={activeDate}
        onChange={(e) => handleDateChange(e.target.value)}
        className={SELECT_CLS}
      >
        <option value="">All Dates</option>
        {DAYS.map((d) => (
          <option key={d} value={d}>{d.replace('_', ' ')}</option>
        ))}
      </select>

      <span className="text-border shrink-0">|</span>

      {/* Match search */}
      <label className="text-[10px] text-slate-500 uppercase tracking-wider shrink-0">Match</label>
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search by ID…"
        className="bg-panel border border-border rounded px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-accent placeholder-slate-600 w-36"
      />

      <select
        value={selectedMatch ?? ''}
        onChange={(e) => { setSelectedMatch(e.target.value || null); setSearch('') }}
        disabled={isLoading}
        className={`${SELECT_CLS} flex-1 min-w-0`}
      >
        <option value="">
          {isLoading ? 'Loading…' : `— ${filtered.length} match${filtered.length !== 1 ? 'es' : ''} —`}
        </option>
        {filtered.map((m) => (
          <option key={m.match_id} value={m.match_id}>
            {m.match_id.slice(0, 8)}…{m.match_id.slice(-4)}
            {'  ·  '}{m.date.replace('_', ' ')}
            {'  ·  '}👤{m.human_count} 🤖{m.bot_count} ⚔{m.kill_count}
          </option>
        ))}
      </select>

      {selectedMatch && (
        <button
          onClick={() => { setSelectedMatch(null); setSearch('') }}
          className="text-slate-600 hover:text-slate-400 text-xs shrink-0 transition-colors"
          title="Clear match"
        >
          ✕
        </button>
      )}
    </div>
  )
}
