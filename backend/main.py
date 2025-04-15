from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
import numpy as np
import random
import requests

app = FastAPI(
    title="EPL Prediction Engine API",
    description="Predicts Premier League standings and team performances",
    version="1.0.0"
)

from backend.api import transfers
app.include_router(transfers.router)

print("Loading EPL Prediction API...")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data path and attempt to load data
DATA_PATH = "data/processed/simulated_season_history.csv"
try:
    df = pd.read_csv(DATA_PATH)
    seasons = sorted(df["Season"].unique())
    print(f"Loaded data with {len(seasons)} seasons")
except Exception as e:
    print(f"Error loading data: {str(e)}")
    # Create dummy data if file not found
    seasons = ["2025/2026", "2026/2027", "2027/2028", "2028/2029", "2029/2030"]
    df = None

# Mount static directory if it exists
if os.path.exists("backend/static"):
    app.mount("/static", StaticFiles(directory="backend/static"), name="static")
elif os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the frontend application"""
    # Look for index.html in several possible locations
    for path in ["backend/static/index.html", "static/index.html", "frontend/dist/index.html"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    
    # Default message if no frontend is found
    return """
    <html>
        <head><title>EPL Prediction Engine API</title></head>
        <body>
            <h1>EPL Prediction Engine API</h1>
            <p>API is running. Frontend not found.</p>
            <p>Available endpoints:</p>
            <ul>
                <li><a href="/standings?season=2027/2028">/standings?season=YYYY/YYYY</a></li>
                <li><a href="/team?season=2027/2028&team=Arsenal">/team?season=YYYY/YYYY&team=TeamName</a></li>
                <li><a href="/seasons">/seasons</a> (List all available seasons)</li>
                <li><a href="/teams?season=2027/2028">/teams?season=YYYY/YYYY</a> (List all teams in a season)</li>
            </ul>
        </body>
    </html>
    """

@app.get("/standings")
def get_standings(season: str = Query(..., description="Season in format YYYY/YYYY")):
    """Get the league standings for a specific season"""
    if df is None:
        # Return dummy data if no data file
        return generate_dummy_standings()
    
    try:
        # Get standings from real data if available
        if season not in seasons:
            season = seasons[-1]  # Use latest season if requested one not found
            
        standings = df[df["Season"] == season].copy()
        
        # Calculate match stats if they don't exist
        if "Matches" not in standings.columns:
            standings["Matches"] = 38
        
        # Ensure Win/Draw/Loss columns exist
        if "Win" not in standings.columns or "Draw" not in standings.columns or "Loss" not in standings.columns:
            # Approximate wins and draws based on points
            standings["Win"] = (standings["Points"] * 0.8 / 3).round().astype(int)
            standings["Draw"] = (standings["Points"] * 0.2 / 1).round().astype(int) 
            standings["Loss"] = standings["Matches"] - standings["Win"] - standings["Draw"]
        
        # Sort by points in descending order
        standings = standings.sort_values(by=["Points"], ascending=False)
        
        result = []
        for idx, row in standings.iterrows():
            win_rate = round((row["Win"] / row["Matches"]) * 100, 1)
            goals_scored = row["GF"] if "GF" in row else None
            goals_conceded = row["GA"] if "GA" in row else None
            clean_sheets = max(1, round(38 - (goals_conceded / 2))) if goals_conceded else None
            possession = min(65, max(35, round(45 + random.uniform(-5, 5))))

            result.append({
                "Team": row["Team"],
                "Points": row["Points"],
                "Matches": row["Matches"],
                "Win": row["Win"],
                "Draw": row["Draw"],
                "Loss": row["Loss"],
                "PredictedRank": len(result) + 1,
                "WinRate": win_rate,
                "GoalsScored": goals_scored,
                "GoalsConceded": goals_conceded,
                "CleanSheets": clean_sheets,
                "Possession": possession
            })

        return result
    except Exception as e:
        print(f"Error in get_standings: {str(e)}")
        # Return dummy data if any error occurs
        return generate_dummy_standings()

@app.get("/team")
def get_team_details(
    season: str = Query(..., description="Season in format YYYY/YYYY"),
    team: str = Query(..., description="Team name")
):
    """Get detailed stats for a specific team in a specific season"""
    if df is None:
        # Return dummy data if no data file
        return generate_dummy_team_data(team)
    
    try:
        # Get team data from real data if available
        if season not in seasons:
            season = seasons[-1]
            
        team_data = df[(df["Season"] == season) & (df["Team"] == team)]
        
        if team_data.empty:
            # Team not found, return dummy data
            return generate_dummy_team_data(team)
        
        # Get the team data as a dictionary
        data = team_data.iloc[0].to_dict()
        
        team_list = df[df["Season"] == season].copy()
        team_list = team_list.sort_values(by=["Points"], ascending=False).reset_index(drop=True)
        rank_map = {row["Team"]: idx + 1 for idx, row in team_list.iterrows()}
        data["PredictedRank"] = rank_map.get(team, None)

        # Add and format additional fields for frontend
        enhance_team_data(data)
        # Set up API details
        API_KEY = os.getenv("API_FOOTBALL_KEY")
        BASE_URL = "https://v3.football.api-sports.io"
        headers = {"x-apisports-key": API_KEY}
        team_name = data["Team"]
        season_year = season.split("/")[0]
 
        # Fetch team ID early before other API calls
        team_id = None
        try:
            team_search = requests.get(
                f"{BASE_URL}/teams",
                params={"search": team_name},
                headers=headers,
                timeout=5
            )
            team_data = team_search.json()
            team_id = team_data["response"][0]["team"]["id"]
        except Exception as e:
            print(f"Error fetching team ID for {team_name}: {e}")

        # Fetch top scorer
        try:
            scorer_resp = requests.get(
                f"{BASE_URL}/players/topscorers",
                params={"league": 39, "season": season_year},
                headers=headers,
                timeout=5
            )
            top_players = scorer_resp.json()["response"]
            top_scorer = next((p for p in top_players if p["statistics"][0]["team"]["name"] == team_name), None)
            if top_scorer:
                data["TopScorer"] = {
                    "name": top_scorer["player"]["name"],
                    "goals": top_scorer["statistics"][0]["goals"]["total"]
                }
        except Exception as e:
            print(f"Error fetching top scorer for {team_name}: {e}")

        # Transfers (if team_id available)
        try:
            if team_id:
                trans_resp = requests.get(
                    f"{BASE_URL}/transfers",
                    params={"team": team_id},
                    headers=headers,
                    timeout=5
                )
                transfers = trans_resp.json()["response"]
                data["TransfersIn"] = [{"name": t["player"]["name"], "from": t["transfers"][0]["teams"]["in"]["name"], "fee": t["transfers"][0]["type"]} for t in transfers if "in" in t["transfers"][0]["teams"]]
                data["TransfersOut"] = [{"name": t["player"]["name"], "to": t["transfers"][0]["teams"]["out"]["name"], "fee": t["transfers"][0]["type"]} for t in transfers if "out" in t["transfers"][0]["teams"]]
        except Exception as e:
            print(f"Error fetching transfers for {team_name}: {e}")

        return data
    except Exception as e:
        print(f"Error in get_team_details: {str(e)}")
        # Return dummy data if any error occurs
        return generate_dummy_team_data(team)

@app.get("/seasons")
def get_seasons():
    """Get all available seasons in the dataset"""
    return {"seasons": seasons}

@app.get("/teams")
def get_teams(season: str = Query(..., description="Season in format YYYY/YYYY")):
    """Get all teams for a specific season"""
    if df is None:
        # Return dummy teams if no data file
        teams = generate_dummy_standings()
        return {"teams": [team["Team"] for team in teams]}
    
    try:
        if season not in seasons:
            season = seasons[-1]
            
        teams = df[df["Season"] == season]["Team"].unique().tolist()
        return {"teams": teams}
    except Exception as e:
        print(f"Error in get_teams: {str(e)}")
        # Return dummy teams if any error occurs
        teams = generate_dummy_standings()
        return {"teams": [team["Team"] for team in teams]}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0", "dataLoaded": df is not None}

@app.get("/team-squad")
def get_team_squad(team: str = Query(..., description="Team name")):
    """Get full squad data for a team using API-Football"""
    try:
        API_KEY = os.getenv("API_FOOTBALL_KEY")
        BASE_URL = "https://v3.football.api-sports.io"
        headers = {"x-apisports-key": API_KEY}

        # Step 1: Search for team ID
        team_search = requests.get(
            f"{BASE_URL}/teams",
            params={"search": team},
            headers=headers,
            timeout=5
        )
        team_data = team_search.json()
        if not team_data.get("response"):
            raise HTTPException(status_code=404, detail="Team not found")

        team_id = team_data["response"][0]["team"]["id"]

        # Step 2: Fetch squad
        squad_resp = requests.get(
            f"{BASE_URL}/players/squads",
            params={"team": team_id},
            headers=headers,
            timeout=5
        )
        squad_data = squad_resp.json().get("response", [])
        if not squad_data:
            raise HTTPException(status_code=404, detail="No squad data available")

        players = squad_data[0].get("players", [])
        formatted = [{
            "name": p.get("name"),
            "age": p.get("age"),
            "number": p.get("number"),
            "position": p.get("position"),
            "nationality": p.get("nationality")
        } for p in players]

        return formatted

    except Exception as e:
        print(f"Error in get_team_squad: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Helper functions to generate dummy data
def generate_dummy_standings():
    """Load predicted standings from simulated_season_history.csv"""
    try:
        df_simulated = pd.read_csv("data/processed/simulated_season_history.csv")
        latest_season = sorted(df_simulated["Season"].unique())[-1]
        standings = df_simulated[df_simulated["Season"] == latest_season].copy()

        if "Win" not in standings.columns:
            standings["Win"] = (standings["Points"] * 0.8 / 3).round().astype(int)
        if "Draw" not in standings.columns:
            standings["Draw"] = (standings["Points"] * 0.2 / 1).round().astype(int)
        if "Loss" not in standings.columns:
            standings["Loss"] = 38 - standings["Win"] - standings["Draw"]

        standings = standings.sort_values(by="Points", ascending=False)

        results = []
        for idx, row in standings.iterrows():
            results.append({
                "Team": row["Team"],
                "Points": row["Points"],
                "Matches": 38,
                "Win": row["Win"],
                "Draw": row["Draw"],
                "Loss": row["Loss"]
            })

        return results
    except Exception as e:
        print(f"Error loading simulated predictions: {e}")
        return []

def generate_dummy_team_data(team):
    """Generate dummy team data when API's data source is unavailable"""
    top_teams = ["Man City", "Liverpool", "Arsenal", "Chelsea", "Man United", "Tottenham"]
    mid_teams = ["Aston Villa", "Newcastle", "West Ham", "Brighton", "Brentford", "Wolves", "Crystal Palace"]
    
    is_top_team = team in top_teams
    is_mid_team = team in mid_teams
    
    # Base statistics depending on team tier
    if is_top_team:
        points = random.randint(70, 90)
        win_rate = random.randint(60, 80)
        goals_scored = random.randint(70, 95)
        goals_conceded = random.randint(30, 45)
        clean_sheets = random.randint(12, 18)
        possession = random.randint(55, 65)
        manager_rating = round(random.uniform(0.8, 0.95), 2)
        tier_score = 3
        avg_points = random.randint(70, 85)
        relegation_risk = "None"
        predicted_rank = random.randint(1, 6)
    elif is_mid_team:
        points = random.randint(45, 65)
        win_rate = random.randint(40, 55)
        goals_scored = random.randint(45, 65)
        goals_conceded = random.randint(45, 60)
        clean_sheets = random.randint(8, 14)
        possession = random.randint(45, 55)
        manager_rating = round(random.uniform(0.7, 0.85), 2)
        tier_score = 2
        avg_points = random.randint(45, 60)
        relegation_risk = "Low"
        predicted_rank = random.randint(7, 14)
    else:
        points = random.randint(25, 40)
        win_rate = random.randint(20, 40)
        goals_scored = random.randint(30, 45)
        goals_conceded = random.randint(60, 80)
        clean_sheets = random.randint(3, 8)
        possession = random.randint(35, 45)
        manager_rating = round(random.uniform(0.6, 0.75), 2)
        tier_score = 1
        avg_points = random.randint(25, 40)
        relegation_risk = random.choice(["Medium", "High"])
        predicted_rank = random.randint(15, 20)
    
    return {
        "Team": team,
        "Points": points,
        "winRate": win_rate,
        "goalsScored": goals_scored,
        "goalsConceded": goals_conceded,
        "cleanSheets": clean_sheets,
        "possession": possession,
        "managerRating": manager_rating,
        "tierScore": tier_score,
        "avgPoints": avg_points,
        "relegationRisk": relegation_risk,
        "predictedRank": predicted_rank
    }

def enhance_team_data(data):
    """Add and format additional fields to team data for frontend use"""
    # Add win rate if missing
    if "winRate" not in data and "Win" in data and "Matches" in data:
        data["winRate"] = round((data["Win"] / data["Matches"]) * 100)
    
    # Add clean sheets if missing
    if "cleanSheets" not in data:
        if "GA" in data:
            data["cleanSheets"] = max(1, round(38 - (data["GA"] / 2)))
        else:
            data["cleanSheets"] = random.randint(5, 15)
    
    # Add possession if missing
    if "possession" not in data:
        if "TierScore" in data:
            base = 45 + (data["TierScore"] * 5)
            data["possession"] = min(65, max(35, round(base + random.uniform(-5, 5))))
        else:
            data["possession"] = random.randint(45, 60)
    
    # Add predicted rank if missing
    if "predictedRank" not in data and "PredictedRank" in data:
        data["predictedRank"] = data["PredictedRank"]
    
    # Rename fields for frontend consistency
    if "GF" in data and "goalsScored" not in data:
        data["goalsScored"] = data["GF"]
    
    if "GA" in data and "goalsConceded" not in data:
        data["goalsConceded"] = data["GA"]
    
    if "AvgPoints3Yrs" in data and "avgPoints" not in data:
        data["avgPoints"] = data["AvgPoints3Yrs"]
    
    # Convert relegation risk to text
    if "RelegationRisk" in data and "relegationRisk" not in data:
        risk_value = data["RelegationRisk"]
        if risk_value < 20:
            data["relegationRisk"] = "None"
        elif risk_value < 40:
            data["relegationRisk"] = "Low"
        elif risk_value < 60:
            data["relegationRisk"] = "Medium"
        else:
            data["relegationRisk"] = "High"

if __name__ == "__main__":
    # Only used during development - in production, use uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)