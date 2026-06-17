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

  const players = useMemo(() => {
    if (!data) return []
    return data.players.filter((p) => {
      if (!showBots && p.is_bot) return false
      if (!showHumans && !p.is_bot) return false
      return true
    })
  }, [data, showBots, showHumans])

  useEffect(() => {
    if (layerRef.current) {
      layerRef.current.clearLayers()
    } else {
      layerRef.current = L.layerGroup().addTo(map)
    }

    players.forEach((player) => {
      const pts = playbackMs > 0
        ? player.points.filter((p) => p.ts_elapsed_ms <= playbackMs)
        : player.points

      if (pts.length < 2) return

      const latlngs = pts.map((p) => pixelToLatLng(p.px, p.py))
      const color = player.is_bot ? BOT_COLOR : HUMAN_COLOR
      const poly = L.polyline(latlngs, {
        color,
        weight: player.is_bot ? 1 : 2,
        opacity: player.is_bot ? 0.4 : 0.75,
        smoothFactor: 1.5,
      })
      poly.bindTooltip(
        `${player.is_bot ? '🤖' : '👤'} ${player.user_id.slice(0, 8)}…`,
        { sticky: true },
      )
      layerRef.current!.addLayer(poly)

      // Draw start marker for human players
      if (!player.is_bot && pts[0]) {
        L.circleMarker(pixelToLatLng(pts[0].px, pts[0].py), {
          radius: 4,
          color: '#22c55e',
          fillColor: '#22c55e',
          fillOpacity: 1,
          weight: 0,
        }).addTo(layerRef.current!)
      }
    })

    return () => {
      layerRef.current?.clearLayers()
    }
  }, [players, playbackMs, map])

  return null
}
