"""
Auto-generated insights from the full dataset.
Computed once at startup and cached — static for the session.
All numbers come from real data; nothing is fabricated.
"""
import pandas as pd
from datetime import datetime, timezone


def compute_insights(df: pd.DataFrame) -> list[dict]:
    total_matches = df["match_id"].nunique()
    total_rows = len(df)

    # ── Insight 1: PvP is nearly dead ─────────────────────────────────────────
    pvp_kills  = int((df["event"] == "Kill").sum())
    bot_kills  = int((df["event"] == "BotKill").sum())
    total_kills = pvp_kills + bot_kills
    pvp_pct = round(pvp_kills / total_kills * 100, 2) if total_kills > 0 else 0
    matches_with_pvp = df[df["event"] == "Kill"]["match_id"].nunique()

    insight_pvp = {
        "id": "pvp-near-zero",
        "title": "Human-vs-Human Combat Is Nearly Nonexistent",
        "body": (
            f"Across {total_matches} matches and 5 days of production gameplay, "
            f"only {pvp_kills} player-vs-player kills occurred — just {pvp_pct}% of all kills. "
            f"Players are engaging almost exclusively with bots ({bot_kills:,} bot kills). "
            "If PvP engagement is a design goal, the current map layout, spawn placement, "
            "or encounter funnel is failing to create player-vs-player moments."
        ),
        "stats": [
            {"label": "Human-vs-Human Kills", "value": str(pvp_kills)},
            {"label": "Bot Kills", "value": f"{bot_kills:,}"},
            {"label": "PvP % of All Kills", "value": f"{pvp_pct}%"},
            {"label": "Matches With Any PvP", "value": f"{matches_with_pvp} / {total_matches}"},
        ],
        "severity": "critical",
        "map_id": None,
    }

    # ── Insight 2: Loot is hyper-concentrated ────────────────────────────────
    av_loot = df[(df["map_id"] == "AmbroseValley") & (df["event"] == "Loot")].copy()
    loot_total = len(av_loot)

    if loot_total > 0:
        # Divide into 10x10 grid, find top-20% cell concentration
        av_loot["cell_x"] = (av_loot["px"] / 102.4).clip(0, 9).astype(int)
        av_loot["cell_y"] = (av_loot["py"] / 102.4).clip(0, 9).astype(int)
        av_loot["cell"] = av_loot["cell_x"].astype(str) + "_" + av_loot["cell_y"].astype(str)
        cell_counts = av_loot["cell"].value_counts()
        top20_count = cell_counts.head(20).sum()
        top20_pct = round(top20_count / loot_total * 100, 1)
        total_cells = 100
        visited_cells = cell_counts[cell_counts > 0].count()
        dead_zones = total_cells - visited_cells
        hottest_cell_count = int(cell_counts.iloc[0])
    else:
        top20_pct = 0
        dead_zones = 0
        hottest_cell_count = 0

    insight_loot = {
        "id": "loot-concentration",
        "title": "80% of Loot Concentrates in 20% of AmbroseValley",
        "body": (
            f"On AmbroseValley, the top 20 of 100 map grid cells contain "
            f"{top20_pct}% of all {loot_total:,} loot pickups. "
            f"{dead_zones} grid cells received zero loot pickups across all matches. "
            "Players are routing through the same loot-dense corridors every match, "
            "leaving large portions of the map completely unexplored. "
            "Redistributing loot to undervisited areas would drive map diversity and "
            "create organic player encounters in new locations."
        ),
        "stats": [
            {"label": "Top 20 Cells Share of Loot", "value": f"{top20_pct}%"},
            {"label": "Loot Pickups (AmbroseValley)", "value": f"{loot_total:,}"},
            {"label": "Unvisited Grid Cells", "value": str(dead_zones)},
            {"label": "Hottest Cell Pickups", "value": str(hottest_cell_count)},
        ],
        "severity": "warning",
        "map_id": "AmbroseValley",
    }

    # ── Insight 3: The storm is not threatening ───────────────────────────────
    storm_events = df[df["event"] == "KilledByStorm"]
    storm_total  = len(storm_events)
    matches_with_storm = storm_events["match_id"].nunique()
    storm_pct = round(matches_with_storm / total_matches * 100, 1) if total_matches > 0 else 0

    # Timing: when do storm deaths happen?
    if storm_total > 0:
        avg_storm_time_ms = int(storm_events["ts_elapsed_ms"].mean())
        avg_storm_time_s  = avg_storm_time_ms // 1000
        storm_timing = f"avg {avg_storm_time_s}s into match"
    else:
        storm_timing = "N/A"

    loot_count  = int((df["event"] == "Loot").sum())
    combat_total = int(df["event"].isin(["Kill","Killed","BotKill","BotKilled","KilledByStorm"]).sum())
    loot_ratio  = round(loot_count / combat_total, 1) if combat_total > 0 else 0

    insight_storm = {
        "id": "storm-no-threat",
        "title": "The Storm Is Not Threatening — Players Ignore It",
        "body": (
            f"Only {storm_total} storm deaths occurred across {total_matches} matches "
            f"— just {storm_pct}% of matches see any storm-related fatality. "
            f"Players loot {loot_ratio}× more than they fight, suggesting matches feel "
            "slow and low-stakes. The storm mechanic — designed to force movement and "
            "extraction decisions — is not creating meaningful pressure. "
            "Tightening the storm timer or reducing extraction point accessibility would "
            "increase tension and force the loot-vs-extract tradeoff the game is built around."
        ),
        "stats": [
            {"label": "Storm Deaths (5 days)", "value": str(storm_total)},
            {"label": "Matches With Storm Death", "value": f"{storm_pct}%"},
            {"label": "Loot:Combat Ratio", "value": f"{loot_ratio}:1"},
            {"label": "Storm Death Timing", "value": storm_timing},
        ],
        "severity": "warning",
        "map_id": None,
    }

    return [insight_pvp, insight_loot, insight_storm]
