import { useState } from 'react'
import MapView from './components/MapView'
import FilterPanel from './components/FilterPanel'
import MatchDropdown from './components/MatchDropdown'
import MetricsBar from './components/MetricsBar'
import TimelineBar from './components/TimelineBar'
import RightSidebar from './components/RightSidebar'
import InsightsPanel from './components/InsightsPanel'

type RightTab = 'stats' | 'insights'

export default function App() {
  const [rightTab, setRightTab] = useState<RightTab>('stats')

  return (
    <div className="h-screen w-screen flex flex-col bg-panel overflow-hidden">
      {/* Top bar */}
      <header className="h-10 flex items-center justify-between px-4 bg-surface border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-indigo-400 font-bold text-sm tracking-wide">LILA</span>
          <span className="text-slate-500 text-xs">Player Analytics</span>
        </div>
        <div className="text-[10px] text-slate-600">
          Battle Royale · Feb 10–14 · 796 Matches
        </div>
      </header>

      {/* Main body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Filter panel */}
        <aside className="w-44 border-r border-border shrink-0 overflow-hidden">
          <FilterPanel />
        </aside>

        {/* Center: Dropdown + Metrics + Map */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Match dropdown */}
          <div className="h-11 border-b border-border shrink-0">
            <MatchDropdown />
          </div>

          {/* Metrics cards */}
          <div className="h-20 border-b border-border shrink-0">
            <MetricsBar />
          </div>

          {/* Map */}
          <div className="flex-1 overflow-hidden">
            <MapView />
          </div>

          {/* Timeline bar */}
          <div className="h-12 border-t border-border shrink-0">
            <TimelineBar />
          </div>
        </div>

        {/* Right: Stats / Insights */}
        <aside className="w-56 border-l border-border shrink-0 flex flex-col overflow-hidden">
          {/* Tab bar */}
          <div className="flex border-b border-border shrink-0">
            {(['stats', 'insights'] as RightTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setRightTab(tab)}
                className={`flex-1 py-2 text-xs capitalize transition-colors ${
                  rightTab === tab
                    ? 'bg-accent/10 text-white border-b-2 border-accent'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-hidden">
            {rightTab === 'stats' ? <RightSidebar /> : <InsightsPanel />}
          </div>
        </aside>
      </div>
    </div>
  )
}
