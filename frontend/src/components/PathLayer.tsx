import { useEffect, useRef, useMemo } from 'react'
import L from 'leaflet'
import { useMap } from 'react-leaflet'
import { useStore } from '../store'
import { usePlayerPaths } from '../api'
import { pixelToLatLng } from './MapView'

const HUMAN_COLOR = '#60a5fa'
const BOT_COLOR = '#475569'

export default function PathLayer() {
  const { selectedMatch, showBots, showHumans, playbackMs } = useStore()
  const { data } = usePlayerPaths(selectedMatch, showBots)
  const map = useMap()
  const layerRef = useRef<L.LayerGroup | null>(null)
  const polylinesRef = useRef<Map<string, L.Polyline>>(new Map())

  const players = useMemo(() => {
    if (!data) return []
    return data.players.filter((p) => {
      if (!showBots && p.is_bot) return false
      if (!showHumans && !p.is_bot) return false
      return true
    })
  }, [data, showBots, showHumans])

  // Full rebuild only when the player dataset changes
  useEffect(() => {
    if (!layerRef.current) {
      layerRef.current = L.layerGroup().addTo(map)
    } else {
      layerRef.current.clearLayers()
    }
    polylinesRef.current.clear()

    const cutoff = playbackMs > 0 ? playbackMs : Infinity
    players.forEach((player) => {
      const pts = cutoff < Infinity
        ? player.points.filter((p) => p.ts_elapsed_ms <= cutoff)
        : player.points

      const color = player.is_bot ? BOT_COLOR : HUMAN_COLOR
      const poly = L.polyline(
        pts.length >= 2 ? pts.map((p) => pixelToLatLng(p.px, p.py)) : [],
        { color, weight: player.is_bot ? 1 : 2, opacity: player.is_bot ? 0.4 : 0.75, smoothFactor: 1.5 },
      )
      poly.bindTooltip(
        `${player.is_bot ? '🤖' : '👤'} ${player.user_id.slice(0, 8)}…`,
        { sticky: true },
      )
      layerRef.current!.addLayer(poly)
      polylinesRef.current.set(player.user_id, poly)

      if (!player.is_bot && pts[0]) {
        L.circleMarker(pixelToLatLng(pts[0].px, pts[0].py), {
          radius: 4, color: '#22c55e', fillColor: '#22c55e', fillOpacity: 1, weight: 0,
        }).addTo(layerRef.current!)
      }
    })

    return () => { layerRef.current?.clearLayers(); polylinesRef.current.clear() }
  }, [players, map]) // intentionally excludes playbackMs — handled below

  // Update polyline geometry in-place when playback moves (no clearLayers)
  useEffect(() => {
    if (!polylinesRef.current.size) return
    const cutoff = playbackMs > 0 ? playbackMs : Infinity
    players.forEach((player) => {
      const poly = polylinesRef.current.get(player.user_id)
      if (!poly) return
      const pts = cutoff < Infinity
        ? player.points.filter((p) => p.ts_elapsed_ms <= cutoff)
        : player.points
      poly.setLatLngs(pts.length >= 2 ? pts.map((p) => pixelToLatLng(p.px, p.py)) : [])
    })
  }, [playbackMs, players])

  return null
}
