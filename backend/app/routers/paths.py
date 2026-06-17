from fastapi import APIRouter, Depends, Query
from ..dependencies import get_match_index
from ..models.api import PathPoint, PlayerPath, PlayerPathsResponse
from ..config import MOVE_EVENTS

router = APIRouter()


@router.get("/player-paths", response_model=PlayerPathsResponse)
def get_player_paths(
    match_id: str = Query(...),
    include_bots: bool = Query(default=True),
    match_index: dict = Depends(get_match_index),
):
    if match_id not in match_index:
        return PlayerPathsResponse(match_id=match_id, map_id="", players=[], total_players=0)

    df = match_index[match_id]
    pos = df[df["event"].isin(MOVE_EVENTS)].copy()

    if not include_bots:
        pos = pos[~pos["is_bot"]]

    players: list[PlayerPath] = []
    for user_id, grp in pos.groupby("user_id"):
        grp_sorted = grp.sort_values("ts_elapsed_ms")
        points = [
            PathPoint(
                px=float(row.px),
                py=float(row.py),
                ts_elapsed_ms=int(row.ts_elapsed_ms),
            )
            for row in grp_sorted.itertuples(index=False)
        ]
        is_bot = bool(grp["is_bot"].iloc[0])
        players.append(PlayerPath(user_id=str(user_id), is_bot=is_bot, points=points))

    map_id = str(df["map_id"].iloc[0]) if len(df) > 0 else ""
    return PlayerPathsResponse(
        match_id=match_id,
        map_id=map_id,
        players=players,
        total_players=len(players),
    )
