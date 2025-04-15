import pandas as pd
import joblib
import numpy as np

# Load trained model
model = joblib.load("models/final_points_model.pkl")
scaler = joblib.load("models/final_points_scaler.pkl")

def predict_league_standings(team_stats_df):
    """
    Predicts league rankings based on team stats using a trained ML model.
    Returns a DataFrame sorted by predicted rank.
    """
    features = [
        "GF", "GA", "GD", "Win", "Draw", "Loss", "PromotedTeam",
        "ManagerRating", "TierScore", "RelegationRisk", "AvgPoints3Yrs",
        "PrevRank", "SquadAge", "SquadValue", "Injuries", "CleanSheets",
        "ShotsPerGame", "Possession", "PassAccuracy"
    ]
    
    # Defensive check
    for f in features:
        if f not in team_stats_df.columns:
            raise ValueError(f"Missing feature: {f}")

    X = team_stats_df[features].copy()
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    
    np.random.seed(42)
    noise = np.random.normal(loc=0.0, scale=2.0, size=len(preds))
    team_stats_df["PredictedPoints"] = preds + noise
    team_stats_df["PredictedRank"] = team_stats_df["PredictedPoints"].rank(method="min", ascending=False).astype(int)

    return team_stats_df.sort_values(by="PredictedRank")