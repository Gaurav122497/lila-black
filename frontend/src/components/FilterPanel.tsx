import { useStore } from '../store'
import { EVENT_COLORS, HEATMAP_TYPES } from '../constants'
import type { HeatmapType } from '../types'

export default function FilterPanel() {
  const {
    showBots, setShowBots,
    showHumans, setShowHumans,
    showPaths, setShowPaths,
    showEvents, setShowEvents,
    heatmapType, setHeatmapType,
    activeEventTypes, setActiveEventTypes,
  } = useStore()

  function toggleEventType(evt: string) {
    setActiveEventTypes(
      activeEventTypes.includes(evt)
        ? activeEventTypes.filter((x) => x !== evt)
        : [...activeEventTypes, evt],
    )
  }

  return (
    <div className="flex flex-col gap-4 p-4 bg-surface text-sm text-slate-300 overflow-y-auto h-full">
      {/* Layer toggles */}
      <section>
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Layers</h3>
        <div className="flex flex-col gap-2">
          <Toggle label="Events" value={showEvents} onChange={setShowEvents} />
          <Toggle label="Paths" value={showPaths} onChange={setShowPaths} />
          <Toggle label="Humans" value={showHumans} onChange={setShowHumans} color="#60a5fa" />
          <Toggle label="Bots" value={showBots} onChange={setShowBots} color="#475569" />
        </div>
      </section>

      <Divider />

      {/* Event types */}
      <section>
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Event Types</h3>
        <div className="flex flex-col gap-1">
          {Object.entries(EVENT_COLORS).map(([evt, color]) => (
            <label key={evt} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={activeEventTypes.includes(evt)}
                onChange={() => toggleEventType(evt)}
                className="accent-indigo-500"
              />
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
              <span className="text-xs">{evt}</span>
            </label>
          ))}
        </div>
      </section>

      <Divider />

      {/* Heatmap */}
      <section>
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Heatmap</h3>
        <div className="flex flex-col gap-1">
          <button
            onClick={() => setHeatmapType(null)}
            className={`text-left px-3 py-1 rounded text-xs transition-colors ${
              heatmapType === null ? 'bg-accent text-white' : 'hover:bg-border text-slate-400'
            }`}
          >
            Off
          </button>
          {HEATMAP_TYPES.map((t) => (
            <button
              key={t}
              onClick={() => setHeatmapType(t as HeatmapType)}
              className={`text-left px-3 py-1 rounded text-xs capitalize transition-colors ${
                heatmapType === t ? 'bg-accent text-white' : 'hover:bg-border text-slate-400'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}

function Divider() {
  return <div className="border-t border-border" />
}

function Toggle({
  label,
  value,
  onChange,
  color,
}: {
  label: string
  value: boolean
  onChange: (v: boolean) => void
  color?: string
}) {
  return (
    <label className="flex items-center justify-between cursor-pointer">
      <div className="flex items-center gap-2">
        {color && <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />}
        <span className="text-xs">{label}</span>
      </div>
      <input
        type="checkbox"
        checked={value}
        onChange={(e) => onChange(e.target.checked)}
        className="accent-indigo-500"
      />
    </label>
  )
}
