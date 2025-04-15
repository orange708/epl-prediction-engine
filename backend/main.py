from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
from data_service import DataService

print("Loading EPL Prediction API...")

app = FastAPI(
    title="EPL Prediction Engine API",
    description="Predicts Premier League standings and team performances",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data service
try:
    data_service = DataService("data/processed/simulated_season_history.csv")
    print(f"Loaded data with {len(data_service.seasons)} seasons")
except Exception as e:
    print(f"Error loading data: {str(e)}")
    data_service = None

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
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service unavailable")
    
    try:
        return data_service.get_standings(season)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving standings: {str(e)}")

@app.get("/team")
def get_team_details(
    season: str = Query(..., description="Season in format YYYY/YYYY"),
    team: str = Query(..., description="Team name")
):
    """Get detailed stats for a specific team in a specific season"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service unavailable")
    
    try:
        team_data = data_service.get_team_details(season, team)
        if "error" in team_data:
            raise HTTPException(status_code=404, detail=team_data["error"])
        return team_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving team data: {str(e)}")

@app.get("/seasons")
def get_seasons():
    """Get all available seasons in the dataset"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service unavailable")
    
    return {"seasons": data_service.seasons}

@app.get("/teams")
def get_teams(season: str = Query(..., description="Season in format YYYY/YYYY")):
    """Get all teams for a specific season"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="Data service unavailable")
    
    try:
        standings = data_service.get_standings(season)
        return {"teams": [team["Team"] for team in standings]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teams: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    if data_service is None:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "Data service unavailable"}
        )
    
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    # Only used during development - in production, use uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)