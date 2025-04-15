from fastapi import APIRouter, Query, HTTPException
import requests

router = APIRouter()

API_KEY = "b74d8f5aae6213568229f575ed7e0ede"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}


@router.get("/player-stats")
def get_player_stats(team: str = Query(...), season: int = Query(...)):
    # First, get the team ID
    team_search = requests.get(
        f"{BASE_URL}/teams",
        params={"search": team},
        headers=HEADERS,
        timeout=10
    )

    if team_search.status_code != 200:
        raise HTTPException(status_code=team_search.status_code, detail="Failed to fetch team info")

    team_data = team_search.json()
    if not team_data.get("response"):
        raise HTTPException(status_code=404, detail=f"Team '{team}' not found")

    team_id = team_data["response"][0]["team"]["id"]

    # Fetch player statistics
    stats_resp = requests.get(
        f"{BASE_URL}/players",
        params={"team": team_id, "season": season},
        headers=HEADERS,
        timeout=10
    )

    if stats_resp.status_code != 200:
        raise HTTPException(status_code=stats_resp.status_code, detail="Failed to fetch player statistics")

    player_data = stats_resp.json().get("response", [])
    return {"team": team, "season": season, "players": player_data}
