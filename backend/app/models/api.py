"""All Pydantic response models for the FastAPI endpoints."""
from pydantic import BaseModel
from typing import Literal


# ── /maps ─────────────────────────────────────────────────────────────────────
class MapConfig(BaseModel):
    map_id: str
    scale: int
    origin_x: float
    origin_z: float
    minimap_url: str
    total_matches: int
    total_events: int


class MapsResponse(BaseModel):
    maps: list[MapConfig]


# ── /matches ──────────────────────────────────────────────────────────────────
class MatchSummary(BaseModel):
    match_id: str
    map_id: str
    date: str
    human_count: int
    bot_count: int
    total_events: int
    duration_ms: int
    loot_count: int
    kill_count: int


class MatchesResponse(BaseModel):
    matches: list[MatchSummary]
    total: int


# ── /events ───────────────────────────────────────────────────────────────────
class EventRow(BaseModel):
    user_id: str
    event: str
    x: float
    z: float
    px: float
    py: float
    ts_elapsed_ms: int
    is_bot: bool


class EventsResponse(BaseModel):
    match_id: str
    map_id: str
    events: list[EventRow]
    count: int


# ── /player-paths ─────────────────────────────────────────────────────────────
class PathPoint(BaseModel):
    px: float
    py: float
    ts_elapsed_ms: int


class PlayerPath(BaseModel):
    user_id: str
    is_bot: bool
    points: list[PathPoint]


class PlayerPathsResponse(BaseModel):
    match_id: str
    map_id: str
    players: list[PlayerPath]
    total_players: int


# ── /heatmap ──────────────────────────────────────────────────────────────────
class HeatmapResponse(BaseModel):
    map_id: str
    heatmap_type: str
    grid_size: int
    grid: list[float]       # flat row-major, length = grid_size^2, values 0.0-1.0
    max_count: int
    event_count: int


# ── /match-summary ────────────────────────────────────────────────────────────
class EventBreakdown(BaseModel):
    event: str
    count: int


class MatchSummaryDetail(BaseModel):
    match_id: str
    map_id: str
    date: str
    duration_ms: int
    human_count: int
    bot_count: int
    event_breakdown: list[EventBreakdown]
    loot_count: int
    kill_count: int
    pvp_kill_count: int
    bot_kill_count: int
    death_count: int
    storm_death_count: int
    x_min: float
    x_max: float
    z_min: float
    z_max: float


# ── /insights ─────────────────────────────────────────────────────────────────
class InsightStat(BaseModel):
    label: str
    value: str


class Insight(BaseModel):
    id: str
    title: str
    body: str
    stats: list[InsightStat]
    severity: Literal["info", "warning", "critical"]
    map_id: str | None


class InsightsResponse(BaseModel):
    insights: list[Insight]
    generated_at: str
