// ── API response types ────────────────────────────────────────────────────────

export interface MapConfig {
  map_id: string
  scale: number
  origin_x: number
  origin_z: number
  minimap_url: string
  total_matches: number
  total_events: number
}

export interface MapsResponse {
  maps: MapConfig[]
}

export interface MatchSummary {
  match_id: string
  map_id: string
  date: string
  human_count: number
  bot_count: number
  total_events: number
  duration_ms: number
  loot_count: number
  kill_count: number
}

export interface MatchesResponse {
  matches: MatchSummary[]
  total: number
}

export interface EventRow {
  user_id: string
  event: string
  x: number
  z: number
  px: number
  py: number
  ts_elapsed_ms: number
  is_bot: boolean
}

export interface EventsResponse {
  match_id: string
  map_id: string
  events: EventRow[]
  count: number
}

export interface PathPoint {
  px: number
  py: number
  ts_elapsed_ms: number
}

export interface PlayerPath {
  user_id: string
  is_bot: boolean
  points: PathPoint[]
}

export interface PlayerPathsResponse {
  match_id: string
  map_id: string
  players: PlayerPath[]
  total_players: number
}

export interface HeatmapResponse {
  map_id: string
  heatmap_type: string
  grid_size: number
  grid: number[]       // flat [grid_size^2], values 0..1
  max_count: number
  event_count: number
}

export interface EventBreakdown {
  event: string
  count: number
}

export interface MatchSummaryDetail {
  match_id: string
  map_id: string
  date: string
  duration_ms: number
  human_count: number
  bot_count: number
  event_breakdown: EventBreakdown[]
  loot_count: number
  kill_count: number
  pvp_kill_count: number
  bot_kill_count: number
  death_count: number
  storm_death_count: number
  x_min: number
  x_max: number
  z_min: number
  z_max: number
}

export interface InsightStat {
  label: string
  value: string
}

export interface Insight {
  id: string
  title: string
  body: string
  stats: InsightStat[]
  severity: 'info' | 'warning' | 'critical'
  map_id: string | null
}

export interface InsightsResponse {
  insights: Insight[]
  generated_at: string
}

// ── Store types ───────────────────────────────────────────────────────────────

export type HeatmapType = 'kills' | 'deaths' | 'traffic' | 'loot' | null

export interface AppState {
  selectedMap: string
  selectedMatch: string | null
  selectedDates: string[]
  showBots: boolean
  showHumans: boolean
  showPaths: boolean
  showEvents: boolean
  heatmapType: HeatmapType
  playbackMs: number         // current playback position in elapsed ms
  isPlaying: boolean
  activeEventTypes: string[]

  setSelectedMap: (map: string) => void
  setSelectedMatch: (match: string | null) => void
  setSelectedDates: (dates: string[]) => void
  setShowBots: (v: boolean) => void
  setShowHumans: (v: boolean) => void
  setShowPaths: (v: boolean) => void
  setShowEvents: (v: boolean) => void
  setHeatmapType: (t: HeatmapType) => void
  setPlaybackMs: (ms: number | ((prev: number) => number)) => void
  setIsPlaying: (v: boolean) => void
  setActiveEventTypes: (types: string[]) => void
}
