import { useStore } from '../store'
import { useMatchSummary } from '../api'

export default function MetricsBar() {
  const { selectedMatch } = useStore()
  const { data } = useMatchSummary(selectedMatch)

  const total = data ? data.human_count + data.bot_count : null

  return (
    <div className="flex items-stretch gap-3 px-4 h-full">
      <MetricCard
        label="Total Players"
        value={total ?? '—'}
        sub={total !== null ? `${data!.human_count + data!.bot_count} in match` : 'no match selected'}
        color="text-white"
        accent="border-indigo-500/40"
      />
      <MetricCard
        label="Humans"
        value={data?.human_count ?? '—'}
        sub="human players"
        color="text-blue-400"
        accent="border-blue-500/40"
      />
      <MetricCard
        label="Bots"
        value={data?.bot_count ?? '—'}
        sub="bot players"
        color="text-slate-400"
        accent="border-slate-500/40"
      />
      <MetricCard
        label="Kills"
        value={data?.kill_count ?? '—'}
        sub={data ? `${data.pvp_kill_count} PvP · ${data.bot_kill_count} vs Bot` : ''}
        color="text-red-400"
        accent="border-red-500/40"
      />
      <MetricCard
        label="Loot"
        value={data?.loot_count ?? '—'}
        sub="pickup events"
        color="text-green-400"
        accent="border-green-500/40"
      />
      <MetricCard
        label="Duration"
        value={data ? fmtMs(data.duration_ms) : '—'}
        sub={data ? `${data.event_breakdown.reduce((s, e) => s + e.count, 0).toLocaleString()} events` : ''}
        color="text-yellow-400"
        accent="border-yellow-500/40"
      />
    </div>
  )
}

function MetricCard({
  label,
  value,
  sub,
  color,
  accent,
}: {
  label: string
  value: string | number
  sub: string
  color: string
  accent: string
}) {
  return (
    <div className={`flex-1 flex flex-col justify-center bg-surface border rounded px-3 py-2 ${accent}`}>
      <div className="text-[10px] text-slate-500 uppercase tracking-wider">{label}</div>
      <div className={`text-xl font-bold tabular-nums leading-tight ${color}`}>{value}</div>
      <div className="text-[10px] text-slate-600 truncate">{sub}</div>
    </div>
  )
}

function fmtMs(ms: number): string {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  return `${m}:${String(s % 60).padStart(2, '0')}`
}
