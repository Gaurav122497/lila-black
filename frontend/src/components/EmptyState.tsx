import { useStore } from '../store'
import { useMatches } from '../api'

export default function EmptyState() {
  const { selectedMap, selectedDates } = useStore()
  const { data } = useMatches(selectedMap, selectedDates)
  const count = data?.total ?? 0

  return (
    <div className="absolute inset-0 z-[500] flex flex-col items-center justify-center pointer-events-none">
      <div className="bg-black/60 backdrop-blur-sm rounded-2xl px-8 py-6 flex flex-col items-center gap-3 text-center">
        <div className="text-3xl">🗺️</div>
        <div className="text-slate-300 text-sm font-semibold">Select a match to begin</div>
        <div className="text-slate-500 text-xs">
          {count > 0
            ? `${count} matches available for ${selectedMap}`
            : 'Choose a map and date above'}
        </div>
        <div className="flex gap-4 mt-1 text-[10px] text-slate-600">
          <span>↑ Use the dropdowns above</span>
        </div>
      </div>
    </div>
  )
}
