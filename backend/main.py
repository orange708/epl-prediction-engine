from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

print("Loading EPL Prediction API...")

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load once into memory
DATA_PATH = "data/processed/simulated_season_history.csv"
df = pd.read_csv(DATA_PATH)

@app.get("/standings")
def get_standings(season: str = Query(..., description="Season in format YYYY/YYYY")):
    if len(season.split('/')) == 2 and len(season.split('/')[1]) == 2:
        base = season.split('/')[0]
        season = f"{base}/{str(int(base[:2] + season.split('/')[1]))}"
    standings = df[df["Season"] == season].sort_values(by="Points", ascending=False)
    return standings[["Team", "Points"]].to_dict(orient="records")

@app.get("/team")
def get_team_details(season: str, team: str):
    if len(season.split('/')) == 2 and len(season.split('/')[1]) == 2:
        base = season.split('/')[0]
        season = f"{base}/{str(int(base[:2] + season.split('/')[1]))}"
    team_data = df[(df["Season"] == season) & (df["Team"] == team)]
    if team_data.empty:
        return {"error": "Team not found"}
    return team_data.iloc[0].to_dict()

@app.get("/")
def root():
    return {"message": "Welcome to the EPL Prediction API!"}
