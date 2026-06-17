"""
Data loader: reads all parquet files using ThreadPoolExecutor,
cleans and returns a single in-memory DataFrame.

Key decisions:
- ThreadPoolExecutor(8) cuts cold-start from ~12s to ~2-3s
- event column decoded from bytes to str
- is_bot: "-" not in user_id (UUID = human, numeric = bot)
- ts_elapsed_ms computed per match_id group (raw ts is a global counter)
- match_index dict built for O(1) per-match lookup
"""
import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import numpy as np

from ..config import DATA_DIR, DAYS, LOADER_WORKERS
from .transform import world_to_pixel

logger = logging.getLogger(__name__)


def _load_file(path: Path) -> pd.DataFrame | None:
    try:
        df = pd.read_parquet(path)
        df["date"] = path.parent.name
        return df
    except Exception as e:
        logger.warning(f"Could not read {path.name}: {e}")
        return None


def _load_raw() -> pd.DataFrame:
    paths: list[Path] = []
    for day in DAYS:
        day_path = DATA_DIR / day
        if day_path.exists():
            paths.extend(day_path.iterdir())

    logger.info(f"Loading {len(paths)} parquet files with {LOADER_WORKERS} workers...")
    frames: list[pd.DataFrame] = []

    with ThreadPoolExecutor(max_workers=LOADER_WORKERS) as ex:
        futures = {ex.submit(_load_file, p): p for p in paths}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                frames.append(result)

    if not frames:
        raise RuntimeError(f"No parquet files found in {DATA_DIR}")

    return pd.concat(frames, ignore_index=True)


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # Decode bytes event column
    df["event"] = df["event"].apply(
        lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
    )

    # Human vs bot detection
    df["is_bot"] = ~df["user_id"].str.contains("-", na=False)

    # ts is stored as Unix epoch SECONDS but pandas reads it as datetime64[ms],
    # so astype(int64) gives seconds-as-ms units. Multiply by 1000 → true ms.
    df["ts_ms"] = df["ts"].astype("int64") * 1000
    match_min = df.groupby("match_id")["ts_ms"].transform("min")
    df["ts_elapsed_ms"] = (df["ts_ms"] - match_min).astype("int64")

    # Pre-compute pixel coordinates (vectorized, <1ms)
    px_all = np.full(len(df), np.nan)
    py_all = np.full(len(df), np.nan)
    for map_id in df["map_id"].unique():
        mask = df["map_id"] == map_id
        px, py = world_to_pixel(df.loc[mask, "x"].values, df.loc[mask, "z"].values, map_id)
        px_all[mask.values] = px
        py_all[mask.values] = py

    df["px"] = px_all
    df["py"] = py_all

    return df


def load_all() -> pd.DataFrame:
    df = _load_raw()
    df = _clean(df)
    logger.info(f"Loaded {len(df):,} rows across {df['match_id'].nunique()} matches")
    return df


def build_match_index(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """O(1) per-match lookup dict — built once at startup."""
    return {
        mid: grp.reset_index(drop=True)
        for mid, grp in df.groupby("match_id")
    }
