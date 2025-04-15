import pandas as pd
import numpy as np
from src.predictor import predict_league_standings

# Load base season data
df = pd.read_csv("data/processed/team_season_stats.csv")
df = df[df["Season"] == "2024/2025"].copy()

# Define helper features
top_teams = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
promoted_teams = []

# Preserve original 2024/25 as base
base_df = df.copy()

# Simulate and predict for multiple future seasons
for year in range(2025, 2031):
    season = f"{year}/{year+1}"
    season_df = base_df.copy()

    # Evolve stats with stronger variation
    season_df["Points"] *= np.random.uniform(0.90, 1.10, size=len(season_df))
    season_df["GF"] *= np.random.uniform(0.90, 1.10, size=len(season_df))
    season_df["GA"] *= np.random.uniform(0.90, 1.10, size=len(season_df))
    season_df["GD"] = season_df["GF"] - season_df["GA"]
    season_df["Win"] *= np.random.uniform(0.90, 1.10, size=len(season_df))
    season_df["Draw"] *= np.random.uniform(0.90, 1.10, size=len(season_df))
    season_df["Loss"] *= np.random.uniform(0.90, 1.10, size=len(season_df))

    # Round for realism
    season_df[["Points", "GF", "GA", "GD", "Win", "Draw", "Loss"]] = season_df[["Points", "GF", "GA", "GD", "Win", "Draw", "Loss"]].round(1)

    # Add features for prediction
    season_df["Season"] = season
    season_df["PromotedTeam"] = season_df["Team"].apply(lambda t: 1 if t in promoted_teams else 0)
    season_df["ManagerRating"] = season_df["Team"].apply(lambda t: 0.85 if t in top_teams else 0.65)
    season_df["TierScore"] = season_df["Team"].apply(lambda t: 3 if t in top_teams else (1 if t in promoted_teams else 2))
    season_df["RelegationRisk"] = season_df["Points"].max() - season_df["Points"]

    # Predict and print standings
    predicted_table = predict_league_standings(season_df.copy())

    print(f"\nPredicted Standings for {season}:")
    for i, team in enumerate(predicted_table["Team"], 1):
        print(f"{i}. {team}")
