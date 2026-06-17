import { useEffect, useRef } from 'react'
import L from 'leaflet'
import { useMap } from 'react-leaflet'
import { useStore } from '../store'
import { useHeatmap } from '../api'
import { IMG_SIZE } from '../constants'

// Heatmap rendered as a canvas overlay on Leaflet CRS.Simple
export default function HeatmapCanvas() {
  const { selectedMap, heatmapType, selectedMatch } = useStore()
  const { data } = useHeatmap(selectedMap, heatmapType, selectedMatch)
  const map = useMap()
  const overlayRef = useRef<L.ImageOverlay | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(document.createElement('canvas'))

  useEffect(() => {
    if (!data || !heatmapType) return

    const { grid, grid_size } = data
    const canvas = canvasRef.current
    canvas.width = grid_size
    canvas.height = grid_size
    const ctx = canvas.getContext('2d')!

    // Draw each cell — grid is row-major: row=y(down), col=x(right)
    for (let row = 0; row < grid_size; row++) {
      for (let col = 0; col < grid_size; col++) {
        const val = grid[row * grid_size + col]
        if (val < 0.02) continue  // skip near-zero cells for clarity
        ctx.fillStyle = valueToColor(val)
        ctx.fillRect(col, row, 1, 1)
      }
    }

    const dataUrl = canvas.toDataURL()

    const bounds: L.LatLngBoundsExpression = [[0, 0], [IMG_SIZE, IMG_SIZE]]
    if (overlayRef.current) {
      overlayRef.current.setUrl(dataUrl)
    } else {
      overlayRef.current = L.imageOverlay(dataUrl, bounds, { opacity: 0.65, zIndex: 5 }).addTo(map)
    }

    return () => {
      overlayRef.current?.remove()
      overlayRef.current = null
    }
  }, [data, heatmapType, map])

  return null
}

function valueToColor(v: number): string {
  // Blue → Cyan → Green → Yellow → Red
  const stops: [number, [number, number, number]][] = [
    [0,    [0,   0,   255]],
    [0.25, [0,   255, 255]],
    [0.5,  [0,   255, 0  ]],
    [0.75, [255, 255, 0  ]],
    [1,    [255, 0,   0  ]],
  ]
  for (let i = 0; i < stops.length - 1; i++) {
    const [t0, c0] = stops[i]
    const [t1, c1] = stops[i + 1]
    if (v <= t1) {
      const t = (v - t0) / (t1 - t0)
      const r = Math.round(c0[0] + t * (c1[0] - c0[0]))
      const g = Math.round(c0[1] + t * (c1[1] - c0[1]))
      const b = Math.round(c0[2] + t * (c1[2] - c0[2]))
      const a = Math.round(180 + v * 75)  // alpha 180-255
      return `rgba(${r},${g},${b},${a / 255})`
    }
  }
  return 'rgba(255,0,0,1)'
}
