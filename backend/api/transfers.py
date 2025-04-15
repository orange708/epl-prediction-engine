from fastapi import APIRouter, Query
from src.api_fetchers.transfer_fetcher import get_team_transfers, TEAM_ID_MAP

router = APIRouter()

@router.get("/transfers")
def fetch_transfers(team: str = Query(...), season: int = Query(...)):
    team_id = TEAM_ID_MAP.get(team)
    if not team_id:
        return {"error": f"Unknown team: {team}"}

    transfers = get_team_transfers(team_id, season)
    return transfers