"""
Constants and configuration for all 3 maps.
Single source of truth — never duplicate these values.
"""
from pathlib import Path
import os

# ── Data paths ────────────────────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BACKEND_DIR / "player_data")))
STATIC_DIR = BACKEND_DIR / "static"
MINIMAP_DIR = STATIC_DIR / "minimaps"

DAYS = [
    "February_10",
    "February_11",
    "February_12",
    "February_13",
    "February_14",
]

# ── Map configuration (from README, validated Phase 1) ────────────────────────
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370.0, "origin_z": -473.0},
    "GrandRift":     {"scale": 581,  "origin_x": -290.0, "origin_z": -290.0},
    "Lockdown":      {"scale": 1000, "origin_x": -500.0, "origin_z": -500.0},
}

MAPS = list(MAP_CONFIG.keys())
IMG_SIZE = 1024

MINIMAP_EXT = {
    "AmbroseValley": "png",
    "GrandRift":     "png",
    "Lockdown":      "jpg",
}

# ── Event groupings ────────────────────────────────────────────────────────────
ALL_EVENTS    = ["Position", "BotPosition", "Kill", "Killed", "BotKill", "BotKilled", "KilledByStorm", "Loot"]
HUMAN_EVENTS  = ["Position", "Kill", "Killed", "BotKill", "BotKilled", "KilledByStorm", "Loot"]
BOT_EVENTS    = ["BotPosition"]
KILL_EVENTS   = ["Kill", "BotKill"]
DEATH_EVENTS  = ["Killed", "BotKilled", "KilledByStorm"]
COMBAT_EVENTS = ["Kill", "Killed", "BotKill", "BotKilled", "KilledByStorm"]
MOVE_EVENTS   = ["Position", "BotPosition"]

HEATMAP_EVENT_MAP = {
    "kills":   KILL_EVENTS,
    "deaths":  DEATH_EVENTS,
    "traffic": MOVE_EVENTS,
    "loot":    ["Loot"],
}

# ── Concurrency ───────────────────────────────────────────────────────────────
LOADER_WORKERS = 8
