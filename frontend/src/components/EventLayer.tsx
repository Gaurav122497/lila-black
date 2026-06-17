import { useMemo, useRef, useEffect } from 'react'
import { useStore } from '../store'
import { useEvents } from '../api'
import { EVENT_COLORS, EVENT_RADIUS } from '../constants'
import { pixelToLatLng } from './MapView'
import L from 'leaflet'
import { useMap } from 'react-leaflet'

type EventRow = { event: string; is_bot: boolean; px: number; py: number; ts_elapsed_ms: number }

const sharedRenderer = L.canvas({ padding: 0.5 })

function makeMarker(e: EventRow): L.CircleMarker {
  const color = EVENT_COLORS[e.event] ?? '#888'
  const radius = EVENT_RADIUS[e.event] ?? 4
  const m = L.circleMarker(pixelToLatLng(e.px, e.py), {
    radius,
    color,
    fillColor: color,
    fillOpacity: e.is_bot ? 0.5 : 0.85,
    weight: e.is_bot ? 0 : 1.5,
    renderer: sharedRenderer,
  })
  m.bindTooltip(
    `<b>${e.event}</b><br>${e.is_bot ? '🤖 Bot' : '👤 Human'}<br>t+${(e.ts_elapsed_ms / 1000).toFixed(1)}s`,
    { sticky: true, className: 'map-tooltip' },
  )
  return m
}

export default function EventLayer() {
  const { selectedMatch, showBots, showHumans, activeEventTypes, playbackMs } = useStore()
  const { data } = useEvents(selectedMatch, activeEventTypes, showBots)
  const map = useMap()

  const layerRef = useRef<L.LayerGroup | null>(null)
  const sortedRef = useRef<EventRow[]>([])
  const renderedUpToRef = useRef<number>(0)
  const prevPlaybackRef = useRef<number>(-1)
  const justRebuiltRef = useRef(false)

  // Pre-sorted events without playback cutoff applied
  const staticFiltered = useMemo(() => {
    if (!data) return []
    return data.events
      .filter((e) => {
        if (!activeEventTypes.includes(e.event)) return false
        if (!showBots && e.is_bot) return false
        if (!showHumans && !e.is_bot) return false
        return true
      })
      .sort((a, b) => a.ts_elapsed_ms - b.ts_elapsed_ms)
  }, [data, activeEventTypes, showBots, showHumans])

  // Full rebuild when data or filters change
  useEffect(() => {
    if (!layerRef.current) {
      layerRef.current = L.layerGroup().addTo(map)
    } else {
      layerRef.current.clearLayers()
    }
    sortedRef.current = staticFiltered
    renderedUpToRef.current = 0
    justRebuiltRef.current = true

    const cutoff = playbackMs > 0
      ? staticFiltered.findIndex((e) => e.ts_elapsed_ms > playbackMs)
      : staticFiltered.length
    const end = cutoff === -1 ? staticFiltered.length : cutoff

    for (let i = 0; i < end; i++) {
      layerRef.current.addLayer(makeMarker(staticFiltered[i]))
    }
    renderedUpToRef.current = end
    prevPlaybackRef.current = playbackMs

    return () => { layerRef.current?.clearLayers() }
  }, [staticFiltered, map]) // intentionally excludes playbackMs — handled below

  // Incremental update when only playbackMs changes
  useEffect(() => {
    // Skip if the rebuild effect just ran this cycle (it already applied playbackMs)
    if (justRebuiltRef.current) {
      justRebuiltRef.current = false
      return
    }
    const layer = layerRef.current
    const sorted = sortedRef.current
    if (!layer || sorted.length === 0) return

    if (playbackMs === 0) {
      // Show all
      for (let i = renderedUpToRef.current; i < sorted.length; i++) {
        layer.addLayer(makeMarker(sorted[i]))
      }
      renderedUpToRef.current = sorted.length
    } else if (playbackMs >= prevPlaybackRef.current) {
      // Forward: add only newly visible markers
      const prev = renderedUpToRef.current
      let end = prev
      while (end < sorted.length && sorted[end].ts_elapsed_ms <= playbackMs) end++
      for (let i = prev; i < end; i++) {
        layer.addLayer(makeMarker(sorted[i]))
      }
      renderedUpToRef.current = end
    } else {
      // Backward scrub: full rebuild to cutoff
      layer.clearLayers()
      const cutoff = sorted.findIndex((e) => e.ts_elapsed_ms > playbackMs)
      const end = cutoff === -1 ? sorted.length : cutoff
      for (let i = 0; i < end; i++) {
        layer.addLayer(makeMarker(sorted[i]))
      }
      renderedUpToRef.current = end
    }

    prevPlaybackRef.current = playbackMs
  }, [playbackMs])

  return null
}
