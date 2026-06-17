from fastapi import APIRouter, Depends, Query
import pandas as pd

from ..dependencies import get_df
from ..models.api import MatchSummary, MatchesResponse
from ..config import DAYS

router = APIRouter()


@router.get("/matches", response_model=MatchesResponse)
def get_matches(
    map_id: str = Query(...),
    date: list[str] = Query(default=DAYS),
    df: pd.DataFrame = Depends(get_df),
):
    mask = (df["map_id"] == map_id) & (df["date"].isin(date))
    filtered = df[mask]

    if filtered.empty:
        return MatchesResponse(matches=[], total=0)

    summaries = []
    for match_id, grp in filtered.groupby("match_id"):
        summaries.append(MatchSummary(
            match_id=str(match_id),
            map_id=str(grp["map_id"].iloc[0]),
            date=str(grp["date"].iloc[0]),
            human_count=int((~grp["is_bot"]).sum() and grp[~grp["is_bot"]]["user_id"].nunique()),
            bot_count=int(grp[grp["is_bot"]]["user_id"].nunique()),
            total_events=int(len(grp)),
            duration_ms=int(grp["ts_elapsed_ms"].max()),
            loot_count=int((grp["event"] == "Loot").sum()),
            kill_count=int(grp["event"].isin(["Kill", "BotKill"]).sum()),
        ))

    # Sort newest date first, then by match_id
    summaries.sort(key=lambda m: (m.date, m.match_id), reverse=True)
    return MatchesResponse(matches=summaries, total=len(summaries))
