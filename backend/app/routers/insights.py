from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone
from ..dependencies import get_insights
from ..models.api import Insight, InsightStat, InsightsResponse

router = APIRouter()


@router.get("/insights", response_model=InsightsResponse)
def get_insights_route(
    map_id: str | None = Query(default=None),
    insights_data: list[dict] = Depends(get_insights),
):
    filtered = [
        i for i in insights_data
        if map_id is None or i["map_id"] is None or i["map_id"] == map_id
    ]

    insights = [
        Insight(
            id=i["id"],
            title=i["title"],
            body=i["body"],
            stats=[InsightStat(label=s["label"], value=s["value"]) for s in i["stats"]],
            severity=i["severity"],
            map_id=i["map_id"],
        )
        for i in filtered
    ]

    return InsightsResponse(
        insights=insights,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
