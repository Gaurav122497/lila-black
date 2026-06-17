"""
Heatmap computation: bins pixel coordinates into a density grid.
Uses np.histogram2d — fast enough for 89k rows in <5ms.
"""
import numpy as np
import pandas as pd
from functools import lru_cache

from ..config import IMG_SIZE, HEATMAP_EVENT_MAP, MAPS


def compute_heatmap(
    px: np.ndarray,
    py: np.ndarray,
    grid_size: int = 64,
) -> tuple[list[float], int]:
    """
    Bin pixel coordinates into a grid_size x grid_size density grid.
    Returns (flat_normalized_grid, max_count).
    Grid is row-major (row=y, col=x), normalized 0.0-1.0.
    """
    if len(px) == 0:
        return [0.0] * (grid_size * grid_size), 0

    grid, _, _ = np.histogram2d(
        px, py,
        bins=grid_size,
        range=[[0, IMG_SIZE], [0, IMG_SIZE]],
    )
    max_count = int(grid.max())
    if max_count == 0:
        return [0.0] * (grid_size * grid_size), 0

    normalized = (grid / max_count).T.flatten().tolist()
    return normalized, max_count


def precompute_map_heatmaps(df: pd.DataFrame) -> dict[tuple[str, str, int], tuple[list[float], int]]:
    """
    Pre-compute all 12 map-level heatmaps at startup:
    3 maps x 4 heatmap types x 1 default grid size = 12 grids.
    Keyed by (map_id, heatmap_type, grid_size).
    """
    cache: dict[tuple[str, str, int], tuple[list[float], int]] = {}
    grid_size = 64

    for map_id in MAPS:
        map_df = df[df["map_id"] == map_id]
        for htype, events in HEATMAP_EVENT_MAP.items():
            sub = map_df[map_df["event"].isin(events)]
            result = compute_heatmap(sub["px"].values, sub["py"].values, grid_size)
            cache[(map_id, htype, grid_size)] = result

    return cache
