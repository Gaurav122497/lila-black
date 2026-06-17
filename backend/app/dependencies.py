"""FastAPI dependency injection — provides app state to route handlers."""
from fastapi import Request
import pandas as pd


def get_df(request: Request) -> pd.DataFrame:
    return request.app.state.df


def get_match_index(request: Request) -> dict[str, pd.DataFrame]:
    return request.app.state.match_index


def get_heatmap_cache(request: Request) -> dict:
    return request.app.state.heatmap_cache


def get_insights(request: Request) -> list[dict]:
    return request.app.state.insights
