"""
Coordinate transform: game world (x, z) -> minimap pixel (px, py).

Formula (from README, validated Phase 1 — 100% in-bounds on all 3 maps):
    u       = (x - origin_x) / scale
    v       = (z - origin_z) / scale
    pixel_x = u * 1024
    pixel_y = (1 - v) * 1024    <- Y flipped: image origin top-left

In Leaflet CRS.Simple (used by the React frontend):
    latLng = [1024 - pixel_y, pixel_x]   <- Leaflet lat=y, lng=x, Y increases upward
"""
import numpy as np
from ..config import MAP_CONFIG, IMG_SIZE


def world_to_pixel(
    x: np.ndarray | float,
    z: np.ndarray | float,
    map_id: str,
) -> tuple[np.ndarray, np.ndarray]:
    cfg = MAP_CONFIG[map_id]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    px = u * IMG_SIZE
    py = (1.0 - v) * IMG_SIZE
    return px, py


def pixel_to_world(
    px: float,
    py: float,
    map_id: str,
) -> tuple[float, float]:
    """Inverse transform — used for hover tooltip reverse lookup."""
    cfg = MAP_CONFIG[map_id]
    u = px / IMG_SIZE
    v = 1.0 - (py / IMG_SIZE)
    x = u * cfg["scale"] + cfg["origin_x"]
    z = v * cfg["scale"] + cfg["origin_z"]
    return x, z
