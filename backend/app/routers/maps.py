from fastapi import APIRouter, Depends
import pandas as pd

from ..dependencies import get_df
from ..models.api import MapConfig, MapsResponse
from ..config import MAP_CONFIG, MINIMAP_EXT

router = APIRouter()


@router.get("/maps", response_model=MapsResponse)
def get_maps(df: pd.DataFrame = Depends(get_df)):
    maps = []
    for map_id, cfg in MAP_CONFIG.items():
        ext = MINIMAP_EXT[map_id]
        map_df = df[df["map_id"] == map_id]
        maps.append(MapConfig(
            map_id=map_id,
            scale=cfg["scale"],
            origin_x=cfg["origin_x"],
            origin_z=cfg["origin_z"],
            minimap_url=f"/static/minimaps/{map_id}_Minimap.{ext}",
            total_matches=int(map_df["match_id"].nunique()),
            total_events=int(len(map_df)),
        ))
    return MapsResponse(maps=maps)
