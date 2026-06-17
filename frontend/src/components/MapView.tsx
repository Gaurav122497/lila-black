import { useMemo, useRef, useEffect } from 'react'
import { MapContainer, ImageOverlay, useMap } from 'react-leaflet'
import L from 'leaflet'
import { useStore } from '../store'
import { useMaps, useEvents } from '../api'
import EventLayer from './EventLayer'
import PathLayer from './PathLayer'
import HeatmapCanvas from './HeatmapCanvas'
import MapLegend from './MapLegend'
import EmptyState from './EmptyState'
import { IMG_SIZE } from '../constants'

// Leaflet CRS.Simple: lat = image-y (0=top), lng = image-x (0=left)
// Our pixel coords: px ∈ [0,1024], py ∈ [0,1024] where py=0 is map-top
// → leaflet latLng = [1024 - py, px]  (Leaflet lat increases upward)
export function pixelToLatLng(px: number, py: number): L.LatLng {
  return L.latLng(IMG_SIZE - py, px)
}

const BOUNDS: L.LatLngBoundsExpression = [[0, 0], [IMG_SIZE, IMG_SIZE]]

function ResetView({ mapId }: { mapId: string }) {
  const map = useMap()
  useEffect(() => {
    map.fitBounds(BOUNDS)
  }, [map, mapId])
  return null
}

export default function MapView() {
  const { selectedMap, showEvents, showPaths, heatmapType, selectedMatch, activeEventTypes, showBots } = useStore()
  const { data: mapsData } = useMaps()
  const { isFetching } = useEvents(selectedMatch, activeEventTypes, showBots)
  const mapRef = useRef<L.Map>(null)

  const mapConfig = useMemo(
    () => mapsData?.maps.find((m) => m.map_id === selectedMap),
    [mapsData, selectedMap],
  )

  const minimapUrl = mapConfig
    ? (import.meta.env.VITE_API_URL ?? '') + mapConfig.minimap_url
    : null

  return (
    <div className="relative w-full h-full">
      <MapContainer
        ref={mapRef}
        crs={L.CRS.Simple}
        bounds={BOUNDS}
        minZoom={-2}
        maxZoom={4}
        zoomSnap={0.5}
        className="w-full h-full"
        preferCanvas
      >
        {minimapUrl && (
          <ImageOverlay url={minimapUrl} bounds={BOUNDS} />
        )}

        {heatmapType && <HeatmapCanvas />}
        {showPaths && <PathLayer />}
        {showEvents && <EventLayer />}

        <ResetView mapId={selectedMap} />
      </MapContainer>

      {/* Map name label */}
      <div className="absolute top-2 left-1/2 -translate-x-1/2 z-[1000] bg-black/60 text-white text-xs px-3 py-1 rounded-full pointer-events-none">
        {selectedMap}
      </div>

      {/* Loading spinner */}
      {isFetching && (
        <div className="absolute top-2 right-3 z-[1000] flex items-center gap-1.5 bg-black/60 text-slate-400 text-xs px-2.5 py-1 rounded-full pointer-events-none">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          Loading…
        </div>
      )}

      {/* Empty state */}
      {!selectedMatch && <EmptyState />}

      {/* Legend */}
      <MapLegend />
    </div>
  )
}
