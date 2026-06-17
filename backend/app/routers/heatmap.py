from fastapi import APIRouter, Depends, Query
from ..dependencies import get_df, get_match_index, get_heatmap_cache
from ..models.api import HeatmapResponse
from ..services.heatmap import compute_heatmap
from ..config import HEATMAP_EVENT_MAP
import pandas as pd

router = APIRouter()

VALID_TYPES = list(HEATMAP_EVENT_MAP.keys())


@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(
    map_id: str = Query(...),
    heatmap_type: str = Query(...),
    match_id: str | None = Query(default=None),
    grid_size: int = Query(default=64, ge=16, le=128),
    df: pd.DataFrame = Depends(get_df),
    match_index: dict = Depends(get_match_index),
    heatmap_cache: dict = Depends(get_heatmap_cache),
):
    if heatmap_type not in VALID_TYPES:
        heatmap_type = "kills"

    events = HEATMAP_EVENT_MAP[heatmap_type]

    # Use pre-computed cache for map-level at default grid size
    if match_id is None and grid_size == 64:
        cache_key = (map_id, heatmap_type, 64)
        if cache_key in heatmap_cache:
            grid, max_count = heatmap_cache[cache_key]
            event_count = int(df[(df["map_id"] == map_id) & df["event"].isin(events)].shape[0])
            return HeatmapResponse(
                map_id=map_id, heatmap_type=heatmap_type,
                grid_size=64, grid=grid,
                max_count=max_count, event_count=event_count,
            )

    # Per-match or custom grid size: compute on request
    if match_id and match_id in match_index:
        source = match_index[match_id]
    else:
        source = df[df["map_id"] == map_id]

    sub = source[source["event"].isin(events)]
    grid, max_count = compute_heatmap(sub["px"].values, sub["py"].values, grid_size)

    return HeatmapResponse(
        map_id=map_id, heatmap_type=heatmap_type,
        grid_size=grid_size, grid=grid,
        max_count=max_count, event_count=len(sub),
    )
