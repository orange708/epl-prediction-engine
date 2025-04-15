import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.predictor import predict_league_standings

# Load team stats for a season
df = pd.read_csv("data/processed/team_season_stats.csv")
season = "2024/2025"
df = df[df["Season"] == season]

# Add PromotedTeam flag
promoted_teams = {
    "2024/2025": ["Sunderland", "Ipswich", "Leeds"]
}
df["PromotedTeam"] = df.apply(lambda row: 1 if row["Team"] in promoted_teams.get(season, []) else 0, axis=1)

# Add ManagerRating (simple heuristic)
top_teams = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
df["ManagerRating"] = df["Team"].apply(lambda t: 0.85 if t in top_teams else 0.65)

# Add TierScore
df["TierScore"] = df["Team"].apply(lambda t: 3 if t in top_teams else (1 if df.loc[df["Team"] == t, "PromotedTeam"].iloc[0] == 1 else 2))

# Add RelegationRisk (inverse of points)
df["RelegationRisk"] = df["Points"].max() - df["Points"]

# Prepare features from all seasons
df_all = pd.read_csv("data/processed/team_season_stats.csv")

# Ensure FinalRank exists
if "FinalRank" not in df_all.columns:
    df_all["FinalRank"] = df_all.groupby("Season")["Points"].rank(method="first", ascending=False).astype(int)

# Calculate rolling average of Points over past 3 seasons
df_all["AvgPoints3Yrs"] = df_all.groupby("Team")["Points"].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

# Merge AvgPoints3Yrs for current season
avg_points_map = df_all[df_all["Season"] == season].set_index("Team")["AvgPoints3Yrs"].to_dict()
df["AvgPoints3Yrs"] = df["Team"].map(avg_points_map).fillna(df["Points"].mean())

# Merge PrevRank from previous season
prev_season = "2023/2024"
prev_rank_map = df_all[df_all["Season"] == prev_season].set_index("Team")["FinalRank"].to_dict()
df["PrevRank"] = df["Team"].map(prev_rank_map).fillna(21)

# Predict standings using trained model
predicted_table = predict_league_standings(df)

# Print results
print(f"\nPredicted Standings for {season}:")
for i, team in enumerate(predicted_table["Team"], 1):
    print(f"{i}. {team}")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Serve frontend static files
app.mount("/static", StaticFiles(directory="backend/static", html=True), name="static")

# Serve index.html for all other routes
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa():
    index_path = Path("backend/static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return {"detail": "Frontend not found."}