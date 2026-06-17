"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR
from .services.loader import load_all, build_match_index
from .services.heatmap import precompute_map_heatmaps
from .services.insights import compute_insights
from .routers import maps, matches, events, paths, heatmap, summary, insights

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading data...")
    df = load_all()
    app.state.df = df
    app.state.match_index = build_match_index(df)
    app.state.heatmap_cache = precompute_map_heatmaps(df)
    app.state.insights = compute_insights(df)
    logger.info(f"Ready — {len(df):,} events, {len(app.state.match_index)} matches")
    yield
    # Nothing to clean up


app = FastAPI(
    title="LILA Games Player Analytics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Static files (minimaps)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Routers
app.include_router(maps.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(paths.router, prefix="/api")
app.include_router(heatmap.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(insights.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
