import pandas as pd
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

# Predict standings using trained model
predicted_table = predict_league_standings(df)

# Print results
print(f"\nPredicted Standings for {season}:")
for i, team in enumerate(predicted_table["Team"], 1):
    print(f"{i}. {team}")