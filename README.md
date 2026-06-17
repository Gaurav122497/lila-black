# LILA Games — Player Analytics Tool

A production-quality web application for Level Designers to visualise player behaviour from Battle Royale match telemetry. Built as a take-home assignment for the Product Engineer role at LILA Games.

**Live demo:** _[Railway + Vercel URLs after deployment]_

---

## Features

| Feature | Detail |
|---------|--------|
| **Player journeys** | Movement paths per player, colour-coded human (blue) vs bot (grey) |
| **Event markers** | Kill, Death, Storm Death, Loot — distinct colours + sizes, canvas-rendered for performance |
| **Heatmap overlays** | Kills / Deaths / Traffic / Loot density on 64×64 grid |
| **Timeline playback** | Scrub or auto-play a match at 5× speed; markers appear as the match unfolds |
| **Match filters** | Filter by map, date (Feb 10–14), bot/human toggle, event type |
| **Match selector** | Browse all 796 matches with summary stats (humans, bots, kills) |
| **Match stats panel** | Per-match breakdown: event counts, PvP kills, storm deaths, loot |
| **Data insights** | 3 real findings from the dataset with supporting statistics |

## Tech Stack

**Frontend:** React 18 · TypeScript · Vite · TailwindCSS · React Leaflet · TanStack Query v5 · Zustand

**Backend:** FastAPI · Pydantic v2 · Pandas · NumPy · PyArrow · Apache Parquet

**Deploy:** Vercel (frontend) · Railway (backend)

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Player data in `backend/player_data/` (or set `DATA_DIR` env var)

### Backend

```bash
cd backend
pip install -r requirements.txt
DATA_DIR=/path/to/player_data uvicorn app.main:app --port 8001 --reload
```

API will be available at `http://localhost:8001`. Docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App will be at `http://localhost:5173`. The Vite dev server proxies `/api` and `/static` to the backend on `:8001`.

## Data

- **Source:** 5 days of match telemetry (Feb 10–14), Apache Parquet files
- **Events:** 89,104 across 796 matches on 3 maps
- **Maps:** AmbroseValley (566 matches), Lockdown (171), GrandRift (59)
- **Player types:** UUID-format user IDs = human players; short numeric IDs = bots
- **Bot detection:** `"-" not in user_id`
- **Timestamps:** `ts` is a global ms counter — normalised per match as `ts - min(ts)`

See [ARCHITECTURE.md](ARCHITECTURE.md) for coordinate transform details and [INSIGHTS.md](INSIGHTS.md) for data findings.

## Project Structure

```
lila-black/
├── backend/
│   ├── app/
│   │   ├── config.py          # MAP_CONFIG, event groupings, DATA_DIR
│   │   ├── main.py            # FastAPI app, lifespan startup
│   │   ├── dependencies.py    # DI: get_df, get_match_index, etc.
│   │   ├── models/api.py      # Pydantic response models
│   │   ├── routers/           # 7 route handlers
│   │   └── services/
│   │       ├── loader.py      # ThreadPoolExecutor parquet loading
│   │       ├── transform.py   # world_to_pixel coordinate transform
│   │       ├── heatmap.py     # np.histogram2d grid computation
│   │       └── insights.py    # 3 data-backed findings
│   ├── static/minimaps/       # 3 map images
│   ├── player_data/           # Parquet files (gitignored if large)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Layout shell
│   │   ├── store.ts           # Zustand UI state
│   │   ├── api.ts             # TanStack Query hooks
│   │   ├── types.ts           # TypeScript interfaces
│   │   └── components/
│   │       ├── MapView.tsx    # Leaflet CRS.Simple container
│   │       ├── EventLayer.tsx # Canvas-rendered event markers
│   │       ├── PathLayer.tsx  # Player movement polylines
│   │       ├── HeatmapCanvas.tsx  # Canvas→ImageOverlay heatmap
│   │       ├── FilterPanel.tsx    # Left sidebar filters
│   │       ├── MatchSelector.tsx  # Match list strip
│   │       ├── TimelineBar.tsx    # RAF playback scrubber
│   │       ├── RightSidebar.tsx   # Match stats panel
│   │       └── InsightsPanel.tsx  # Data insights accordion
│   └── package.json
├── ARCHITECTURE.md
├── INSIGHTS.md
└── README.md
```
