import pandas as pd
import joblib

# Load trained model
model = joblib.load("models/final_rank_model.pkl")
scaler = joblib.load("models/final_rank_scaler.pkl")

def predict_league_standings(team_stats_df):
    """
    Predicts league rankings based on team stats using a trained ML model.
    Returns a DataFrame sorted by predicted rank.
    """
    features = ["Points", "GF", "GA", "GD", "Win", "Draw", "Loss", "PromotedTeam", "ManagerRating", "TierScore", "RelegationRisk"]
    
    # Defensive check
    for f in features:
        if f not in team_stats_df.columns:
            raise ValueError(f"Missing feature: {f}")

    X = team_stats_df[features].copy()
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    team_stats_df["PredictedRank"] = preds

    return team_stats_df.sort_values(by="PredictedRank")