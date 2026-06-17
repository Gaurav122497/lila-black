import { useMemo } from 'react'
import { useStore } from '../store'
import { useEvents } from '../api'
import { EVENT_COLORS, EVENT_RADIUS } from '../constants'
import { pixelToLatLng } from './MapView'
import L from 'leaflet'
import { useMap } from 'react-leaflet'
import { useEffect, useRef } from 'react'

// Uses canvas renderer for performance — handles 12k+ markers without freezing
export default function EventLayer() {
  const { selectedMatch, showBots, showHumans, activeEventTypes, playbackMs } = useStore()
  const { data } = useEvents(selectedMatch, activeEventTypes, showBots)
  const map = useMap()
  const layerRef = useRef<L.LayerGroup | null>(null)

  const filtered = useMemo(() => {
    if (!data) return []
    return data.events.filter((e) => {
      if (!activeEventTypes.includes(e.event)) return false
      if (!showBots && e.is_bot) return false
      if (!showHumans && !e.is_bot) return false
      if (playbackMs > 0 && e.ts_elapsed_ms > playbackMs) return false
      return true
    })
  }, [data, activeEventTypes, showBots, showHumans, playbackMs])

  useEffect(() => {
    if (layerRef.current) {
      layerRef.current.clearLayers()
    } else {
      layerRef.current = L.layerGroup().addTo(map)
    }

    const renderer = L.canvas({ padding: 0.5 })
    filtered.forEach((e) => {
      const color = EVENT_COLORS[e.event] ?? '#888'
      const radius = EVENT_RADIUS[e.event] ?? 4
      const circle = L.circleMarker(pixelToLatLng(e.px, e.py), {
        radius,
        color,
        fillColor: color,
        fillOpacity: e.is_bot ? 0.5 : 0.85,
        weight: e.is_bot ? 0 : 1.5,
        renderer,
      })
      circle.bindTooltip(
        `<b>${e.event}</b><br>${e.is_bot ? '🤖 Bot' : '👤 Human'}<br>ts+${e.ts_elapsed_ms}ms`,
        { sticky: true, className: 'map-tooltip' },
      )
      layerRef.current!.addLayer(circle)
    })

    return () => {
      layerRef.current?.clearLayers()
    }
  }, [filtered, map])

  return null
}
