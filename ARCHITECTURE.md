# Architecture

## System Overview

```
Browser (Vercel)                 Railway (FastAPI)
┌─────────────────────┐          ┌──────────────────────────┐
│  React 18 + TS      │          │  FastAPI + Pydantic v2   │
│  Vite + Tailwind    │◄────────►│  Pandas + NumPy          │
│  React Leaflet      │  HTTP    │  Apache Parquet loader   │
│  TanStack Query v5  │          │  ThreadPoolExecutor(8)   │
│  Zustand            │          └──────────────────────────┘
└─────────────────────┘
```

## Coordinate Mapping

The most critical technical challenge is mapping game-world coordinates to minimap pixel positions. The game engine uses a right-handed coordinate system where Z increases northward; the minimap image has its origin at the top-left with Y increasing downward. This requires a Y-axis flip.

### Formula

```
u  = (x - origin_x) / scale          # normalise x → [0, 1]
v  = (z - origin_z) / scale          # normalise z → [0, 1]
px = u × 1024                         # pixel column (left→right)
py = (1 - v) × 1024                  # pixel row (top→bottom) ← Y FLIP
```

### Map-specific parameters (from official README)

| Map | scale | origin_x | origin_z |
|-----|-------|----------|----------|
| AmbroseValley | 900 | -370 | -473 |
| GrandRift | 581 | -290 | -290 |
| Lockdown | 1000 | -500 | -500 |

### Leaflet CRS.Simple mapping

Leaflet's `CRS.Simple` treats `latLng = [y, x]` with latitude increasing upward. Since our pixel coordinate `py` increases downward (top = 0), the Leaflet LatLng is:

```
L.latLng(1024 - py, px)
```

This was validated empirically: 100% of all 89,104 events land within `[0, 1024] × [0, 1024]` on all three maps after transformation.

## Data Pipeline

```
player_data/
  February_10/ ... February_14/
    *.nakama-0          ← Apache Parquet (no .parquet extension)

ThreadPoolExecutor(8)   ← parallel file loading (~2s vs ~12s serial)
  ↓
DataFrame._clean()
  - decode bytes event names
  - is_bot = "-" not in user_id   (UUID = human, numeric = bot)
  - ts_elapsed_ms = ts_ms - match_min_ts  (normalise per match)
  - px, py pre-computed vectorised
  ↓
build_match_index()     ← dict[match_id → DataFrame] for O(1) lookups
precompute_map_heatmaps() ← 12 grids (3 maps × 4 types) at startup
compute_insights()      ← 3 findings materialised once
```

**Key insight:** `ts` is a global millisecond counter shared across all matches, not wall-clock time. Per-match elapsed time is computed as `ts_ms - min(ts_ms)` within each match group.

## API Design

7 REST endpoints, all read-only GET:

| Endpoint | Purpose | Cache |
|----------|---------|-------|
| `GET /api/maps` | Map configs + aggregate counts | Full startup cache |
| `GET /api/matches` | Match list filtered by map+date | Query-time |
| `GET /api/events` | All events for a match | match_index O(1) |
| `GET /api/player-paths` | Position sequences per player | match_index O(1) |
| `GET /api/heatmap` | 64×64 normalised density grid | Pre-computed |
| `GET /api/match-summary` | Per-match stat breakdown | match_index O(1) |
| `GET /api/insights` | 3 data-backed findings | Startup cache |

## Frontend Architecture

**State split:** Zustand manages UI state (which map, which match, filters, playback position). TanStack Query manages server state (fetching, caching, deduplication).

**Rendering strategy:** React Leaflet with `preferCanvas: true` and a canvas renderer on every `circleMarker`. At 12k+ markers, DOM-based markers freeze the browser; canvas compositing handles this in a single GPU draw.

**Heatmap rendering:** The 64×64 density grid from the API is drawn onto an off-screen `<canvas>`, converted to a data URL, and served as a Leaflet `ImageOverlay`. This avoids 4,096 individual DOM elements.

**Playback:** A `requestAnimationFrame` loop increments `playbackMs` at 5× real speed. `EventLayer` and `PathLayer` filter their data by `ts_elapsed_ms <= playbackMs`, so markers appear incrementally as the match unfolds.

## Trade-offs

| Decision | Alternative | Reason chosen |
|----------|-------------|---------------|
| CRS.Simple + custom image | Tile server (MapTiler) | No internet dependency; exact pixel control |
| Canvas renderer | SVG/DOM markers | DOM freezes at 12k+ markers |
| Pre-computed heatmaps | On-demand computation | Sub-10ms response vs 200ms compute |
| Parquet in-process | PostgreSQL | No DB infra needed; fits in Railway RAM |
| Flat DataFrame + match_index | Per-file lazy loading | Single load at startup, O(1) per-match access |
| match_index dict | Query-time groupby | Avoids repeated 89k-row scans per request |

## Deployment

- **Backend:** Railway — uvicorn, `DATA_DIR` env var points to `backend/player_data/`
- **Frontend:** Vercel — static build, `VITE_API_URL` env var set to Railway URL
- **CORS:** `allow_origins=["*"]` with GET-only — appropriate for a read-only analytics tool
