import { useStore } from '../store'
import { useMatchSummary } from '../api'

export default function RightSidebar() {
  const { selectedMatch } = useStore()
  const { data, isLoading } = useMatchSummary(selectedMatch)

  if (!selectedMatch) {
    return (
      <div className="p-4 text-xs text-slate-600 text-center">
        <p className="mt-8">Select a match from the list</p>
        <p className="mt-2">to see stats here</p>
      </div>
    )
  }

  if (isLoading) {
    return <div className="p-4 text-xs text-slate-600">Loading…</div>
  }

  if (!data) return null

  return (
    <div className="p-4 flex flex-col gap-4 text-sm overflow-y-auto h-full">
      <section>
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Match</h3>
        <div className="text-[10px] font-mono text-slate-400 break-all">{data.match_id}</div>
        <div className="text-xs text-slate-500 mt-1">{data.date.replace('_', ' ')} · {data.map_id}</div>
      </section>

      <StatGrid>
        <Stat label="Humans" value={data.human_count} color="text-blue-400" />
        <Stat label="Bots" value={data.bot_count} color="text-slate-500" />
        <Stat label="PvP Kills" value={data.pvp_kill_count} color="text-red-400" />
        <Stat label="Storm Deaths" value={data.storm_death_count} color="text-purple-400" />
        <Stat label="Loot" value={data.loot_count} color="text-green-400" />
        <Stat label="Duration" value={fmtMs(data.duration_ms)} />
      </StatGrid>

      <section>
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Event Breakdown</h3>
        <div className="flex flex-col gap-1">
          {data.event_breakdown
            .sort((a, b) => b.count - a.count)
            .map(({ event, count }) => (
              <div key={event} className="flex items-center justify-between text-xs">
                <span className="text-slate-400">{event}</span>
                <span className="text-slate-300 tabular-nums">{count.toLocaleString()}</span>
              </div>
            ))}
        </div>
      </section>
    </div>
  )
}

function StatGrid({ children }: { children: React.ReactNode }) {
  return <div className="grid grid-cols-2 gap-2">{children}</div>
}

function Stat({ label, value, color = 'text-slate-200' }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="bg-panel rounded p-2">
      <div className="text-[10px] text-slate-500">{label}</div>
      <div className={`text-sm font-semibold ${color} tabular-nums`}>{value}</div>
    </div>
  )
}

function fmtMs(ms: number): string {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  return `${m}:${String(s % 60).padStart(2, '0')}`
}
