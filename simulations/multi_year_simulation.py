import pandas as pd
import numpy as np
import random
from src.predictor import predict_league_standings

# Load base season data (2024/25)
df = pd.read_csv("data/processed/team_season_stats.csv")
df = df[df["Season"] == "2024/2025"].copy()

# Define top teams and initial promoted pool
top_teams = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
championship_pool = [
    "Sunderland", "Leeds", "Watford", "Norwich", "Sheffield United",
    "Blackburn", "Ipswich", "West Brom", "Stoke", "Bristol City"
]

# Preserve original as base for evolution
base_df = df.copy()
current_teams = base_df["Team"].tolist()

history = {}
season_datasets = {}

for year in range(2025, 2031):
    season = f"{year}/{year+1}"
    season_df = base_df.copy()

    # Evolve stats
    for col in ["Points", "GF", "GA", "Win", "Draw", "Loss"]:
        season_df[col] *= np.random.uniform(0.9, 1.1, size=len(season_df))
    season_df["GD"] = season_df["GF"] - season_df["GA"]
    season_df = season_df.round(1)

    # Apply realism adjustments
    season_df["Season"] = season
    season_datasets[season] = season_df.copy()
    season_df["PromotedTeam"] = season_df["Team"].apply(lambda t: 1 if t not in current_teams else 0)
    season_df["ManagerRating"] = season_df["Team"].apply(lambda t: 0.85 if t in top_teams else 0.65)
    season_df["TierScore"] = season_df["Team"].apply(lambda t: 3 if t in top_teams else (1 if t not in current_teams else 2))
    season_df["RelegationRisk"] = season_df["Points"].max() - season_df["Points"]

    # Predict standings
    predicted = predict_league_standings(season_df.copy())
    history[season] = predicted[["Team", "PredictedRank"]]

    print(f"\nPredicted Standings for {season}:")
    for i, team in enumerate(predicted["Team"], 1):
        print(f"{i}. {team}")

    # Relegate bottom 3
    relegated = predicted.tail(3)["Team"].tolist()
    current_teams = [t for t in predicted["Team"] if t not in relegated]

    # Promote 3 new teams
    promoted = random.sample([t for t in championship_pool if t not in current_teams], 3)
    current_teams.extend(promoted)

    # Create mock stats for promoted teams
    new_teams = pd.DataFrame({
        "Team": promoted,
        "Season": season,
        "Points": np.random.uniform(28, 42, size=3),
        "GF": np.random.uniform(30, 45, size=3),
        "GA": np.random.uniform(55, 70, size=3),
        "Win": np.random.uniform(6, 10, size=3),
        "Draw": np.random.uniform(7, 10, size=3),
        "Loss": np.random.uniform(18, 24, size=3),
    })
    new_teams["GD"] = new_teams["GF"] - new_teams["GA"]
    new_teams["PromotedTeam"] = 1
    new_teams["ManagerRating"] = 0.65
    new_teams["TierScore"] = 1
    new_teams["RelegationRisk"] = new_teams["Points"].max() - new_teams["Points"]

    # Update base_df for next loop
    base_df = pd.concat([season_df[~season_df["Team"].isin(relegated)], new_teams], ignore_index=True)

# Export full multi-season data for team history view
all_seasons_df = pd.concat(season_datasets.values(), ignore_index=True)
all_seasons_df.to_csv("data/processed/simulated_season_history.csv", index=False)
