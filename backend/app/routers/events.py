from fastapi import APIRouter, Depends, Query
from ..dependencies import get_match_index
from ..models.api import EventRow, EventsResponse
from ..config import ALL_EVENTS

router = APIRouter()


@router.get("/events", response_model=EventsResponse)
def get_events(
    match_id: str = Query(...),
    event_type: list[str] = Query(default=ALL_EVENTS),
    include_bots: bool = Query(default=True),
    match_index: dict = Depends(get_match_index),
):
    if match_id not in match_index:
        return EventsResponse(match_id=match_id, map_id="", events=[], count=0)

    df = match_index[match_id]
    mask = df["event"].isin(event_type)
    if not include_bots:
        mask &= ~df["is_bot"]
    sub = df[mask]

    events = [
        EventRow(
            user_id=str(row.user_id),
            event=str(row.event),
            x=float(row.x),
            z=float(row.z),
            px=float(row.px),
            py=float(row.py),
            ts_elapsed_ms=int(row.ts_elapsed_ms),
            is_bot=bool(row.is_bot),
        )
        for row in sub.itertuples(index=False)
    ]

    map_id = str(df["map_id"].iloc[0]) if len(df) > 0 else ""
    return EventsResponse(match_id=match_id, map_id=map_id, events=events, count=len(events))
