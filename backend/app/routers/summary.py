from fastapi import APIRouter, Depends, Query
from ..dependencies import get_match_index
from ..models.api import EventBreakdown, MatchSummaryDetail

router = APIRouter()


@router.get("/match-summary", response_model=MatchSummaryDetail)
def get_match_summary(
    match_id: str = Query(...),
    match_index: dict = Depends(get_match_index),
):
    if match_id not in match_index:
        return MatchSummaryDetail(
            match_id=match_id, map_id="", date="",
            duration_ms=0, human_count=0, bot_count=0,
            event_breakdown=[], loot_count=0,
            kill_count=0, pvp_kill_count=0, bot_kill_count=0,
            death_count=0, storm_death_count=0,
            x_min=0, x_max=0, z_min=0, z_max=0,
        )

    df = match_index[match_id]
    breakdown = [
        EventBreakdown(event=str(evt), count=int(cnt))
        for evt, cnt in df["event"].value_counts().items()
    ]

    return MatchSummaryDetail(
        match_id=match_id,
        map_id=str(df["map_id"].iloc[0]),
        date=str(df["date"].iloc[0]),
        duration_ms=int(df["ts_elapsed_ms"].max()),
        human_count=int(df[~df["is_bot"]]["user_id"].nunique()),
        bot_count=int(df[df["is_bot"]]["user_id"].nunique()),
        event_breakdown=breakdown,
        loot_count=int((df["event"] == "Loot").sum()),
        kill_count=int(df["event"].isin(["Kill", "BotKill"]).sum()),
        pvp_kill_count=int((df["event"] == "Kill").sum()),
        bot_kill_count=int((df["event"] == "BotKill").sum()),
        death_count=int(df["event"].isin(["Killed", "BotKilled", "KilledByStorm"]).sum()),
        storm_death_count=int((df["event"] == "KilledByStorm").sum()),
        x_min=float(df["x"].min()),
        x_max=float(df["x"].max()),
        z_min=float(df["z"].min()),
        z_max=float(df["z"].max()),
    )
