import { EVENT_COLORS } from '../constants'

const LEGEND = [
  { label: 'Human Position', color: EVENT_COLORS.Position, shape: 'circle' },
  { label: 'Bot Position',   color: EVENT_COLORS.BotPosition, shape: 'circle' },
  { label: 'Kill',           color: EVENT_COLORS.Kill, shape: 'circle' },
  { label: 'Death',          color: EVENT_COLORS.Killed, shape: 'circle' },
  { label: 'Storm Death',    color: EVENT_COLORS.KilledByStorm, shape: 'circle' },
  { label: 'Loot',           color: EVENT_COLORS.Loot, shape: 'circle' },
  { label: 'Human Path',     color: '#60a5fa', shape: 'line' },
  { label: 'Bot Path',       color: '#475569', shape: 'line' },
]

export default function MapLegend() {
  return (
    <div className="absolute bottom-3 left-3 z-[1000] bg-black/70 backdrop-blur-sm rounded-lg p-2.5 pointer-events-none">
      <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-1.5">Legend</div>
      <div className="flex flex-col gap-1">
        {LEGEND.map(({ label, color, shape }) => (
          <div key={label} className="flex items-center gap-2">
            {shape === 'circle' ? (
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
            ) : (
              <span className="w-4 h-0.5 shrink-0 rounded" style={{ background: color }} />
            )}
            <span className="text-[10px] text-slate-400">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
