import { create } from 'zustand'
import type { AppState } from './types'

const ALL_EVENTS = ['Position', 'BotPosition', 'Kill', 'Killed', 'BotKill', 'BotKilled', 'KilledByStorm', 'Loot']
const ALL_DATES = ['February_10', 'February_11', 'February_12', 'February_13', 'February_14']

export const useStore = create<AppState>((set) => ({
  selectedMap: 'AmbroseValley',
  selectedMatch: null,
  selectedDates: ALL_DATES,
  showBots: true,
  showHumans: true,
  showPaths: true,
  showEvents: true,
  heatmapType: null,
  playbackMs: 0,
  isPlaying: false,
  activeEventTypes: ALL_EVENTS,

  setSelectedMap: (map) => set({ selectedMap: map, selectedMatch: null, heatmapType: null, playbackMs: 0, isPlaying: false }),
  setSelectedMatch: (match) => set({ selectedMatch: match, playbackMs: 0, isPlaying: false }),
  setSelectedDates: (dates) => set({ selectedDates: dates }),
  setShowBots: (v) => set({ showBots: v }),
  setShowHumans: (v) => set({ showHumans: v }),
  setShowPaths: (v) => set({ showPaths: v }),
  setShowEvents: (v) => set({ showEvents: v }),
  setHeatmapType: (t) => set({ heatmapType: t }),
  setPlaybackMs: (ms) => set((state) => ({
    playbackMs: typeof ms === 'function' ? ms(state.playbackMs) : ms,
  })),
  setIsPlaying: (v) => set({ isPlaying: v }),
  setActiveEventTypes: (types) => set({ activeEventTypes: types }),
}))
