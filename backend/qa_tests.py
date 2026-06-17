"""
QA Data Integrity Tests for LILA Games Player Analytics
Runs directly against the data using the same logic as the backend.
"""
import os
import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import numpy as np

# ── Setup paths ───────────────────────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("DATA_DIR", r"C:\Users\Gaurav\Task - Lila\player_data"))
BACKEND_DIR = Path(r"C:\Users\Gaurav\Task - Lila\lila-black\backend")

# Add backend to path so we can import config/services
sys.path.insert(0, str(BACKEND_DIR))

from app.config import MAP_CONFIG, IMG_SIZE, ALL_EVENTS, DAYS
from app.services.transform import world_to_pixel
from app.services.heatmap import compute_heatmap

# ── Tracking ──────────────────────────────────────────────────────────────────
PASS = []
FAIL = []

def ok(test_name, detail=""):
    PASS.append(test_name)
    print(f"  [PASS] {test_name}" + (f": {detail}" if detail else ""))

def bug(test_name, expected, actual):
    FAIL.append({"test": test_name, "expected": expected, "actual": actual})
    print(f"  [BUG]  {test_name}")
    print(f"         Expected: {expected}")
    print(f"         Actual:   {actual}")


# ════════════════════════════════════════════════════════════════════════════════
# LOAD DATA (same logic as loader.py)
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("LOADING DATA")
print("="*70)

def _load_file(path: Path):
    try:
        df = pd.read_parquet(path)
        df["date"] = path.parent.name
        return df
    except Exception as e:
        print(f"  WARNING: Could not read {path.name}: {e}")
        return None

paths = []
for day in DAYS:
    day_path = DATA_DIR / day
    if day_path.exists():
        paths.extend(day_path.iterdir())

print(f"Found {len(paths)} parquet files across {len(DAYS)} days")

frames = []
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(_load_file, p): p for p in paths}
    for future in as_completed(futures):
        result = future.result()
        if result is not None:
            frames.append(result)

if not frames:
    print("ERROR: No parquet files loaded! Check DATA_DIR.")
    sys.exit(1)

df_raw = pd.concat(frames, ignore_index=True)
print(f"Raw rows loaded: {len(df_raw):,}")

# Apply same cleaning logic as loader._clean()
df_raw["event"] = df_raw["event"].apply(
    lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
)
df_raw["is_bot"] = ~df_raw["user_id"].str.contains("-", na=False)

# Timestamp fix — same code as loader.py
# ts is stored as Unix epoch SECONDS but pandas reads it as datetime64[ms]
# so astype(int64) gives ms-already. But the comment says multiply by 1000...
# Let's capture BOTH what the code does AND what the raw dtype is.
print(f"\nRaw 'ts' column dtype: {df_raw['ts'].dtype}")
sample_ts = df_raw['ts'].iloc[0]
print(f"Sample raw ts value: {sample_ts} (type: {type(sample_ts)})")

# Apply the ACTUAL loader code path
df_raw["ts_ms"] = df_raw["ts"].astype("int64") * 1000
match_min = df_raw.groupby("match_id")["ts_ms"].transform("min")
df_raw["ts_elapsed_ms"] = (df_raw["ts_ms"] - match_min).astype("int64")

# Pixel coordinates
px_all = np.full(len(df_raw), np.nan)
py_all = np.full(len(df_raw), np.nan)
for map_id in df_raw["map_id"].unique():
    mask = df_raw["map_id"] == map_id
    px, py = world_to_pixel(df_raw.loc[mask, "x"].values, df_raw.loc[mask, "z"].values, map_id)
    px_all[mask.values] = px
    py_all[mask.values] = py

df_raw["px"] = px_all
df_raw["py"] = py_all

df = df_raw.copy()
print(f"Final cleaned rows: {len(df):,}")
print(f"Matches: {df['match_id'].nunique()}")
print(f"Maps: {df['map_id'].unique().tolist()}")
print(f"Date range: {df['date'].unique().tolist()}")

# Build match index
match_index = {
    mid: grp.reset_index(drop=True)
    for mid, grp in df.groupby("match_id")
}

# ════════════════════════════════════════════════════════════════════════════════
# TEST 1: COORDINATE TRANSFORM CORRECTNESS
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 1: Coordinate Transform Correctness (all events, all maps)")
print("="*70)

total_events = len(df)
print(f"Total events to check: {total_events:,} (expected ~89,104)")

oob_px = df[(df["px"] < 0) | (df["px"] > 1024)]
oob_py = df[(df["py"] < 0) | (df["py"] > 1024)]
oob_nan_px = df["px"].isna()
oob_nan_py = df["py"].isna()

print(f"\npx range: [{df['px'].min():.4f}, {df['px'].max():.4f}]")
print(f"py range: [{df['py'].min():.4f}, {df['py'].max():.4f}]")
print(f"NaN px count: {oob_nan_px.sum()}")
print(f"NaN py count: {oob_nan_py.sum()}")
print(f"px out-of-bounds (<0 or >1024): {len(oob_px)}")
print(f"py out-of-bounds (<0 or >1024): {len(oob_py)}")

if oob_nan_px.any() or oob_nan_py.any():
    bug("T1-NaN-coords", "No NaN px/py values", f"{oob_nan_px.sum()} NaN px, {oob_nan_py.sum()} NaN py")

if len(oob_px) > 0:
    sample = oob_px[["map_id","x","z","px","py"]].head(5)
    bug("T1-px-out-of-bounds",
        "px in [0, 1024] for all events",
        f"{len(oob_px)} events out of bounds. Sample:\n{sample.to_string()}")
else:
    ok("T1-px-bounds", f"all {total_events:,} px values in [0, 1024]")

if len(oob_py) > 0:
    sample = oob_py[["map_id","x","z","px","py"]].head(5)
    bug("T1-py-out-of-bounds",
        "py in [0, 1024] for all events",
        f"{len(oob_py)} events out of bounds. Sample:\n{sample.to_string()}")
else:
    ok("T1-py-bounds", f"all {total_events:,} py values in [0, 1024]")

# Per-map breakdown
print("\n  Per-map coordinate stats:")
for map_id in df["map_id"].unique():
    mdf = df[df["map_id"] == map_id]
    oob = mdf[(mdf["px"] < 0) | (mdf["px"] > 1024) | (mdf["py"] < 0) | (mdf["py"] > 1024)]
    print(f"    {map_id}: {len(mdf):,} events, {len(oob)} OOB, px=[{mdf['px'].min():.1f},{mdf['px'].max():.1f}], py=[{mdf['py'].min():.1f},{mdf['py'].max():.1f}]")

if total_events == 89104:
    ok("T1-event-count", "exactly 89,104 events")
elif abs(total_events - 89104) < 1000:
    ok("T1-event-count", f"{total_events:,} events (close to expected 89,104)")
else:
    bug("T1-event-count", "~89,104 events", f"{total_events:,} events")


# ════════════════════════════════════════════════════════════════════════════════
# TEST 2: TIMESTAMP FIX — ts_elapsed_ms should be in TRUE milliseconds
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 2: Timestamp Fix — ts_elapsed_ms in TRUE milliseconds")
print("="*70)

TARGET_MATCH = "fbbc5d02-dd79-42fb-bba5-d768023891c8.nakama-0"
print(f"\nTarget match: {TARGET_MATCH}")

if TARGET_MATCH in match_index:
    mdf = match_index[TARGET_MATCH]
    duration_ms = int(mdf["ts_elapsed_ms"].max())
    duration_s = duration_ms / 1000.0
    print(f"  duration_ms (ts_elapsed_ms max): {duration_ms:,}")
    print(f"  duration_s:  {duration_s:.1f}s")
    print(f"  duration:    {int(duration_s//60)}m{int(duration_s%60)}s")

    # Expected: ~523,000ms (8m43s), not 523ms
    if duration_ms > 100_000:  # > 100 seconds is clearly milliseconds
        ok("T2-target-match-duration",
           f"~523,000ms (8m43s), got {duration_ms:,}ms = {duration_s:.0f}s = {int(duration_s//60)}m{int(duration_s%60)}s")
    elif duration_ms < 10_000:  # < 10 seconds is clearly in seconds, not ms
        bug("T2-target-match-duration",
            "~523,000ms (8m43s) — timestamp stored as TRUE milliseconds",
            f"{duration_ms}ms = {duration_s:.1f}s — this is the RAW SECONDS value, NOT milliseconds!")
    else:
        bug("T2-target-match-duration",
            "~523,000ms (8m43s)",
            f"{duration_ms:,}ms = {duration_s:.1f}s (ambiguous range)")
else:
    print(f"  WARNING: Target match {TARGET_MATCH} not found in data!")
    print(f"  Available match IDs (first 10): {list(match_index.keys())[:10]}")

# Check 5 different matches
print("\n  Checking 5 additional matches for sane durations:")
sample_matches = list(match_index.keys())[:5]
sane_count = 0
for mid in sample_matches:
    mdf = match_index[mid]
    dur = int(mdf["ts_elapsed_ms"].max())
    dur_s = dur / 1000.0
    status = "OK" if dur > 30_000 else "SUSPECT (< 30s?)"
    print(f"    {mid[:40]}... -> {dur:,}ms ({dur_s:.1f}s) [{status}]")
    if dur > 30_000:
        sane_count += 1

if sane_count >= 4:
    ok("T2-sample-durations", f"{sane_count}/5 sample matches have plausible ms durations (>30s)")
else:
    bug("T2-sample-durations",
        "5/5 matches with >30s duration (must be ms, not seconds)",
        f"Only {sane_count}/5 matches have >30,000ms — timestamps may be in seconds!")

# Also check raw ts dtype to understand what actually happened
print(f"\n  Raw ts dtype insight:")
print(f"  df['ts'].dtype = {df_raw['ts'].dtype}")
ts_sample = df_raw['ts'].head(3).tolist()
print(f"  First 3 raw ts values: {ts_sample}")
ts_int_sample = df_raw['ts'].astype('int64').head(3).tolist()
print(f"  First 3 as int64:      {ts_int_sample}")
print(f"  After *1000:           {[v*1000 for v in ts_int_sample]}")
# If ts is datetime64[ms], astype(int64) gives ms since epoch, then *1000 = microseconds!
# If ts is datetime64[s], astype(int64) gives seconds since epoch, then *1000 = ms (correct)
if "datetime64" in str(df_raw['ts'].dtype):
    unit = str(df_raw['ts'].dtype)
    print(f"\n  CRITICAL: ts is {unit}!")
    if "[ms]" in unit or "[us]" in unit or "[ns]" in unit:
        print(f"  WARNING: astype(int64) on {unit} gives MILLISECONDS (or finer), then *1000 = WRONG!")
    elif "[s]" in unit:
        print(f"  INFO: astype(int64) on {unit} gives SECONDS, then *1000 = correct ms")


# ════════════════════════════════════════════════════════════════════════════════
# TEST 3: BOT DETECTION
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 3: Bot Detection — is_bot=True means user_id has NO '-' character")
print("="*70)

# Sample 100 rows where is_bot=True
bots = df[df["is_bot"] == True]
humans = df[df["is_bot"] == False]
print(f"  Bot rows:   {len(bots):,}")
print(f"  Human rows: {len(humans):,}")

# Verify bot rule: is_bot=True means no "-" in user_id
sample_bots = bots[["user_id","is_bot"]].drop_duplicates("user_id").head(100)
bot_with_dash = sample_bots[sample_bots["user_id"].str.contains("-", na=False)]
sample_size = len(sample_bots)

print(f"  Sampled {sample_size} unique bot user_ids")
print(f"  Sample bot user_ids (first 5): {sample_bots['user_id'].head(5).tolist()}")

if len(bot_with_dash) == 0:
    ok("T3-bot-no-dash", f"0/{sample_size} bot user_ids contain '-' (rule holds 100%)")
else:
    bug("T3-bot-no-dash",
        "is_bot=True user_ids never contain '-'",
        f"{len(bot_with_dash)}/{sample_size} bot user_ids DO contain '-': {bot_with_dash['user_id'].tolist()[:5]}")

# Verify human rule: is_bot=False means "-" IS in user_id
sample_humans = humans[["user_id","is_bot"]].drop_duplicates("user_id").head(100)
human_without_dash = sample_humans[~sample_humans["user_id"].str.contains("-", na=False)]
human_sample_size = len(sample_humans)

if len(human_without_dash) == 0:
    ok("T3-human-has-dash", f"0/{human_sample_size} human user_ids lack '-' (rule holds 100%)")
else:
    bug("T3-human-has-dash",
        "is_bot=False user_ids always contain '-' (they are UUIDs)",
        f"{len(human_without_dash)}/{human_sample_size} 'human' user_ids have NO '-': {human_without_dash['user_id'].tolist()[:5]}")

# Sample exactly 100 rows (mixed) and verify
sample_100 = df.sample(100, random_state=42)[["user_id","is_bot"]].copy()
sample_100["has_dash"] = sample_100["user_id"].str.contains("-", na=False)
inconsistent = sample_100[sample_100["is_bot"] == sample_100["has_dash"]]  # bot=True but has_dash=True, or bot=False but has_dash=False
if len(inconsistent) == 0:
    ok("T3-sample-100-consistency", "100/100 sampled rows have consistent is_bot vs '-' rule")
else:
    bug("T3-sample-100-consistency",
        "100% consistency: is_bot=True iff user_id has no '-'",
        f"{len(inconsistent)}/100 rows inconsistent: {inconsistent.to_string()}")


# ════════════════════════════════════════════════════════════════════════════════
# TEST 4: EVENT TYPES
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 4: Event Types — only known types should exist")
print("="*70)

known = set(ALL_EVENTS)
actual_types = set(df["event"].unique())
unknown = actual_types - known

print(f"  Known event types:  {sorted(known)}")
print(f"  Actual event types: {sorted(actual_types)}")
print(f"  Unknown types:      {sorted(unknown) if unknown else 'None'}")

counts = df["event"].value_counts()
print(f"\n  Event counts:")
for evt, cnt in counts.items():
    marker = " *** UNKNOWN ***" if evt not in known else ""
    print(f"    {evt}: {cnt:,}{marker}")

if not unknown:
    ok("T4-event-types", f"All {len(actual_types)} event types are known")
else:
    bug("T4-event-types",
        f"Only known types: {sorted(known)}",
        f"Unknown types found: {sorted(unknown)}")


# ════════════════════════════════════════════════════════════════════════════════
# TEST 5: MATCH INDEX
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 5: Match Index — every match_id maps to non-empty DataFrame with correct columns")
print("="*70)

REQUIRED_COLS = {"map_id", "date", "event", "user_id", "x", "z", "px", "py", "ts_elapsed_ms", "is_bot"}

empty_matches = []
missing_cols_matches = []
total_matches = len(match_index)

for mid, mdf in match_index.items():
    if len(mdf) == 0:
        empty_matches.append(mid)
    else:
        actual_cols = set(mdf.columns)
        missing = REQUIRED_COLS - actual_cols
        if missing:
            missing_cols_matches.append({"match_id": mid, "missing": sorted(missing)})

print(f"  Total matches in index: {total_matches:,}")

if empty_matches:
    bug("T5-empty-matches",
        "No empty DataFrames in match index",
        f"{len(empty_matches)} matches are empty: {empty_matches[:5]}")
else:
    ok("T5-empty-matches", f"All {total_matches} matches are non-empty")

if missing_cols_matches:
    bug("T5-column-schema",
        f"All matches have columns: {sorted(REQUIRED_COLS)}",
        f"{len(missing_cols_matches)} matches have missing columns: {missing_cols_matches[:3]}")
else:
    ok("T5-column-schema", f"All {total_matches} matches have the required columns")

# Spot-check a sample match
sample_mid = list(match_index.keys())[0]
sample_mdf = match_index[sample_mid]
print(f"\n  Spot-check match '{sample_mid[:40]}...':")
print(f"    Rows: {len(sample_mdf)}, Columns: {sorted(sample_mdf.columns.tolist())}")


# ════════════════════════════════════════════════════════════════════════════════
# TEST 6: HEATMAP GRID
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 6: Heatmap Grid — output shape is grid_size^2, values 0.0-1.0")
print("="*70)

# Test with known data
test_cases = [
    {"name": "grid_size=64", "grid_size": 64},
    {"name": "grid_size=32", "grid_size": 32},
    {"name": "grid_size=128", "grid_size": 128},
]

# Use real position data from first map
map_id = df["map_id"].iloc[0]
map_df = df[(df["map_id"] == map_id) & (df["event"].isin(["Position","BotPosition"]))]
px_vals = map_df["px"].values
py_vals = map_df["py"].values
print(f"  Using {len(px_vals):,} position events from {map_id}")

for tc in test_cases:
    gs = tc["grid_size"]
    grid, max_count = compute_heatmap(px_vals, py_vals, grid_size=gs)

    expected_len = gs * gs
    actual_len = len(grid)
    min_val = min(grid)
    max_val = max(grid)

    print(f"\n  Test: {tc['name']}")
    print(f"    Expected length: {expected_len}, Actual: {actual_len}")
    print(f"    Value range: [{min_val:.4f}, {max_val:.4f}]")
    print(f"    Max count: {max_count}")

    if actual_len != expected_len:
        bug(f"T6-shape-{gs}", f"grid length = {expected_len} (grid_size^2)", f"got {actual_len}")
    else:
        ok(f"T6-shape-{gs}", f"grid length = {expected_len} as expected")

    if min_val < 0.0 or max_val > 1.0:
        bug(f"T6-values-{gs}", "all values in [0.0, 1.0]", f"range is [{min_val:.4f}, {max_val:.4f}]")
    else:
        ok(f"T6-values-{gs}", f"all values in [{min_val:.4f}, {max_val:.4f}] ⊆ [0.0, 1.0]")

# Test empty input
empty_grid, empty_max = compute_heatmap(np.array([]), np.array([]), grid_size=64)
if len(empty_grid) == 64*64 and all(v == 0.0 for v in empty_grid):
    ok("T6-empty-input", "empty px/py returns 4096 zeros")
else:
    bug("T6-empty-input", f"64^2=4096 zeros", f"got {len(empty_grid)} values, max={max(empty_grid) if empty_grid else 'N/A'}")


# ════════════════════════════════════════════════════════════════════════════════
# TEST 7: INSIGHTS ACCURACY
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("TEST 7: Insights Accuracy")
print("="*70)

from app.services.insights import compute_insights

insights = compute_insights(df)

# 7a: PvP kills (Kill events) count
pvp_actual = int((df["event"] == "Kill").sum())
insight_pvp = next(i for i in insights if i["id"] == "pvp-near-zero")
pvp_stat = next(s for s in insight_pvp["stats"] if s["label"] == "Human-vs-Human Kills")
pvp_reported = int(pvp_stat["value"])

print(f"\n  7a: PvP Kills")
print(f"    Actual Kill events in data: {pvp_actual}")
print(f"    Insight reports:            {pvp_reported}")
print(f"    Constraint check: should be <= 5: {'YES' if pvp_actual <= 5 else 'NO (>5)'}")

if pvp_reported == pvp_actual:
    ok("T7a-pvp-kills-match", f"insight reports {pvp_reported}, data has {pvp_actual} Kill events")
else:
    bug("T7a-pvp-kills-match",
        f"insight PvP kill count = actual data count ({pvp_actual})",
        f"insight says {pvp_reported}")

if pvp_actual <= 5:
    ok("T7a-pvp-kills-leq5", f"PvP kills ({pvp_actual}) <= 5")
else:
    bug("T7a-pvp-kills-leq5", "PvP kills <= 5 (game has almost no PvP)", f"actual: {pvp_actual}")

# 7b: Storm deaths (KilledByStorm)
storm_actual = int((df["event"] == "KilledByStorm").sum())
insight_storm = next(i for i in insights if i["id"] == "storm-no-threat")
storm_stat = next(s for s in insight_storm["stats"] if s["label"] == "Storm Deaths (5 days)")
storm_reported = int(storm_stat["value"])

print(f"\n  7b: Storm Deaths")
print(f"    Actual KilledByStorm events: {storm_actual}")
print(f"    Insight reports:             {storm_reported}")
print(f"    Constraint check: should be <= 50: {'YES' if storm_actual <= 50 else 'NO (>50)'}")

if storm_reported == storm_actual:
    ok("T7b-storm-deaths-match", f"insight reports {storm_reported}, data has {storm_actual}")
else:
    bug("T7b-storm-deaths-match",
        f"insight storm death count = actual ({storm_actual})",
        f"insight says {storm_reported}")

if storm_actual <= 50:
    ok("T7b-storm-deaths-leq50", f"Storm deaths ({storm_actual}) <= 50")
else:
    bug("T7b-storm-deaths-leq50", "Storm deaths <= 50", f"actual: {storm_actual}")

# 7c: Loot concentration plausibility
insight_loot = next(i for i in insights if i["id"] == "loot-concentration")
top20_stat = next(s for s in insight_loot["stats"] if "Top 20" in s["label"])
top20_pct = float(top20_stat["value"].replace("%", ""))
loot_total_stat = next(s for s in insight_loot["stats"] if "Loot Pickups" in s["label"])
loot_total = int(loot_total_stat["value"].replace(",", ""))

# Cross-check: compute ourselves
av_loot = df[(df["map_id"] == "AmbroseValley") & (df["event"] == "Loot")].copy()
actual_loot_total = len(av_loot)

print(f"\n  7c: Loot Concentration (AmbroseValley)")
print(f"    Insight loot total: {loot_total:,}")
print(f"    Actual loot total:  {actual_loot_total:,}")
print(f"    Top-20-cell pct reported: {top20_pct}%")
print(f"    Is top20_pct plausible (>50% means concentration exists): {'YES' if top20_pct > 50 else 'LOW CONCENTRATION'}")
print(f"    Is top20_pct <= 100%: {'YES' if top20_pct <= 100 else 'NO'}")

if loot_total == actual_loot_total:
    ok("T7c-loot-total-match", f"loot count matches: {loot_total:,}")
else:
    bug("T7c-loot-total-match",
        f"insight loot count = actual ({actual_loot_total:,})",
        f"insight says {loot_total:,}")

if 0 <= top20_pct <= 100:
    ok("T7c-loot-pct-range", f"top20 pct = {top20_pct}% (plausible range)")
else:
    bug("T7c-loot-pct-range", "top-20-cell % in [0, 100]", f"got {top20_pct}%")


# ════════════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ════════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("FINAL QA REPORT")
print("="*70)
print(f"\n  PASSED: {len(PASS)}")
for p in PASS:
    print(f"    + {p}")

print(f"\n  BUGS FOUND: {len(FAIL)}")
for i, b in enumerate(FAIL, 1):
    print(f"\n  BUG #{i}: {b['test']}")
    print(f"    Expected: {b['expected']}")
    print(f"    Actual:   {b['actual']}")

if not FAIL:
    print("\n  ALL TESTS PASSED — No bugs found.")
else:
    print(f"\n  {len(FAIL)} BUG(S) DETECTED — see above for details.")

print("\n" + "="*70)
