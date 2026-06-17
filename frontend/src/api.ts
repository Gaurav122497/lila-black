import { useQuery } from '@tanstack/react-query'
import type {
  MapsResponse,
  MatchesResponse,
  EventsResponse,
  PlayerPathsResponse,
  HeatmapResponse,
  MatchSummaryDetail,
  InsightsResponse,
} from './types'

const BASE = import.meta.env.VITE_API_URL ?? ''

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${path}`)
  return res.json() as Promise<T>
}

export function useMaps() {
  return useQuery({
    queryKey: ['maps'],
    queryFn: () => get<MapsResponse>('/api/maps'),
  })
}

export function useMatches(mapId: string, dates: string[]) {
  const q = new URLSearchParams({ map_id: mapId })
  dates.forEach((d) => q.append('date', d))
  return useQuery({
    queryKey: ['matches', mapId, dates],
    queryFn: () => get<MatchesResponse>(`/api/matches?${q}`),
    enabled: !!mapId,
  })
}

export function useEvents(matchId: string | null, eventTypes: string[], showBots: boolean) {
  const q = new URLSearchParams()
  if (matchId) q.set('match_id', matchId)
  eventTypes.forEach((e) => q.append('event_type', e))
  q.set('include_bots', String(showBots))
  return useQuery({
    queryKey: ['events', matchId, eventTypes, showBots],
    queryFn: () => get<EventsResponse>(`/api/events?${q}`),
    enabled: !!matchId,
    placeholderData: (prev) => prev,
  })
}

export function usePlayerPaths(matchId: string | null, showBots: boolean) {
  const q = new URLSearchParams()
  if (matchId) q.set('match_id', matchId)
  q.set('include_bots', String(showBots))
  return useQuery({
    queryKey: ['paths', matchId, showBots],
    queryFn: () => get<PlayerPathsResponse>(`/api/player-paths?${q}`),
    enabled: !!matchId,
    placeholderData: (prev) => prev,
  })
}

export function useHeatmap(mapId: string, heatmapType: string | null, matchId: string | null) {
  const q = new URLSearchParams({ map_id: mapId, heatmap_type: heatmapType ?? 'kills' })
  if (matchId) q.set('match_id', matchId)
  return useQuery({
    queryKey: ['heatmap', mapId, heatmapType, matchId],
    queryFn: () => get<HeatmapResponse>(`/api/heatmap?${q}`),
    enabled: !!heatmapType,
    staleTime: Infinity,
  })
}

export function useMatchSummary(matchId: string | null) {
  return useQuery({
    queryKey: ['summary', matchId],
    queryFn: () => get<MatchSummaryDetail>(`/api/match-summary?match_id=${matchId}`),
    enabled: !!matchId,
  })
}

export function useInsights(mapId?: string) {
  const q = mapId ? `?map_id=${mapId}` : ''
  return useQuery({
    queryKey: ['insights', mapId],
    queryFn: () => get<InsightsResponse>(`/api/insights${q}`),
    staleTime: Infinity,
  })
}
