import pandas as pd
import joblib
import numpy as np
import random

# Load trained model
model = joblib.load("models/final_points_model.pkl")
winner_model = joblib.load("models/final_winner_model.pkl")
scaler = joblib.load("models/final_points_scaler.pkl")

# Constants for team tiers (used for variability)
TOP_TEAMS = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
UPPER_MID_TEAMS = ["Newcastle", "Aston Villa", "West Ham", "Brighton", "Leicester"]
MID_TEAMS = ["Crystal Palace", "Brentford", "Wolves", "Everton", "Southampton", "Fulham"]
LOWER_TEAMS = ["Bournemouth", "Nottingham Forest", "Burnley", "Leeds"]
RELEGATION_CANDIDATES = ["Sheffield United", "Watford", "Norwich", "Ipswich", "Luton", "Sunderland", "Hull"]

# Season-to-season variance factors (to prevent the same team always winning)
TEAM_VARIANCE = {
    "Man City": 0.15,       # More consistent
    "Liverpool": 0.17,
    "Arsenal": 0.18,
    "Chelsea": 0.19,
    "Man United": 0.20,
    "Tottenham": 0.21,
    "Newcastle": 0.22,
    "Aston Villa": 0.23,
    "West Ham": 0.24,
    "Brighton": 0.25,
    "Leicester": 0.25,
    "Crystal Palace": 0.25,
    "Brentford": 0.26,
    "Wolves": 0.26,
    "Everton": 0.27,
    "Southampton": 0.28,
    "Fulham": 0.28, 
    "Bournemouth": 0.28,
    "Nottingham Forest": 0.29,
    "Leeds": 0.30,
    "Burnley": 0.30,
    "Sheffield United": 0.30,
    "Watford": 0.30,
    "Norwich": 0.30,
    "Ipswich": 0.30,
    "Luton": 0.30,
    "Sunderland": 0.30,
    "Hull": 0.30,
}

def get_team_tier(team):
    """Determine which tier a team belongs to"""
    if team in TOP_TEAMS:
        return "top"
    elif team in UPPER_MID_TEAMS:
        return "upper_mid"
    elif team in MID_TEAMS:
        return "mid"
    elif team in LOWER_TEAMS:
        return "lower_mid"
    elif team in RELEGATION_CANDIDATES:
        return "relegation"
    else:
        return "mid"  # Default

def get_variance_factor(team, season_index=0):
    """
    Get the variance factor for a team, which increases over seasons
    to prevent the same team always winning
    """
    base_variance = TEAM_VARIANCE.get(team, 0.25)
    # Increase variance slightly each season
    additional_variance = season_index * 0.02
    return base_variance + additional_variance

def apply_realistic_variance(team, predicted_points, season_index=0):
    """Apply realistic variance to predicted points based on team tier and season"""
    tier = get_team_tier(team)
    variance = get_variance_factor(team, season_index)
    
    # Different tiers have different point ranges
    tier_ranges = {
        "top": {"min": 65, "max": 95},
        "upper_mid": {"min": 52, "max": 70},
        "mid": {"min": 40, "max": 55},
        "lower_mid": {"min": 32, "max": 45},
        "relegation": {"min": 20, "max": 38}
    }
    
    # Add random variance
    volatility = 1.2 - get_team_stability_score(team)
    random_factor = np.random.normal(loc=1.0, scale=variance * volatility)
    adjusted_points = predicted_points * random_factor
    
    # Ensure points are within realistic range for tier
    range_data = tier_ranges[tier]
    adjusted_points = max(range_data["min"], min(range_data["max"], adjusted_points))
    
    return adjusted_points

def add_missing_features(df, season_index=0):
    """
    Add any missing features required by the model with reasonable defaults
    """
    expected_features = [
        "GF", "GA", "GD", "Win", "Draw", "Loss", "PromotedTeam",
        "ManagerRating", "TierScore", "RelegationRisk", "AvgPoints3Yrs",
        "PrevRank", "SquadAge", "SquadValue", "Injuries", "CleanSheets",
        "ShotsPerGame", "Possession", "PassAccuracy"
    ]
    
    for feature in expected_features:
        if feature not in df.columns:
            print(f"Adding missing feature: {feature}")
            
            if feature == "SquadAge":
                # Average age around 25-29
                df[feature] = df["Team"].apply(
                    lambda t: 27 + np.random.normal(0, 1.5)
                )
            elif feature == "SquadValue":
                # Value depends on team tier
                df[feature] = df["Team"].apply(
                    lambda t: 800 + 200 * (3 - tier_to_number(get_team_tier(t))) + np.random.normal(0, 100)
                )
            elif feature == "Injuries":
                # Random number of injuries (1-5)
                df[feature] = np.random.randint(1, 6, size=len(df))
            elif feature == "CleanSheets":
                # Clean sheets correlates with goals against
                if "GA" in df.columns:
                    df[feature] = (38 - df["GA"] / 2).clip(0, 20).astype(int)
                else:
                    df[feature] = np.random.randint(5, 15, size=len(df))
            elif feature == "ShotsPerGame":
                # Shots correlates with team tier
                df[feature] = df["Team"].apply(
                    lambda t: 14 - 2 * tier_to_number(get_team_tier(t)) + np.random.normal(0, 1)
                )
            elif feature == "Possession":
                # Possession correlates with tier
                df[feature] = df["Team"].apply(
                    lambda t: 55 - 5 * tier_to_number(get_team_tier(t)) + np.random.normal(0, 2)
                )
            elif feature == "PassAccuracy":
                # Pass accuracy correlates with tier
                df[feature] = df["Team"].apply(
                    lambda t: 85 - 3 * tier_to_number(get_team_tier(t)) + np.random.normal(0, 1)
                )
            elif feature == "AvgPoints3Yrs":
                # Approximate as current points with some variance
                if "Points" in df.columns:
                    df[feature] = df["Points"] * (0.9 + 0.1 * np.random.random(size=len(df)))
                else:
                    df[feature] = 50.0
            elif feature == "PrevRank":
                # Approximate as inverse of current points
                if "Points" in df.columns:
                    df[feature] = (100 - df["Points"]).rank()
                else:
                    df[feature] = np.random.randint(1, 21, size=len(df))
            
    return df

def tier_to_number(tier):
    """Convert tier string to numeric value for calculations"""
    tier_values = {
        "top": 1,
        "upper_mid": 2,
        "mid": 3,
        "lower_mid": 4,
        "relegation": 5
    }
    return tier_values.get(tier, 3)  # Default to mid-tier

def get_team_stability_score(team):
    # Lower = more volatile; Higher = more stable
    stability_map = {
        "Man City": 0.9, "Liverpool": 0.85, "Arsenal": 0.8, "Chelsea": 0.75,
        "Man United": 0.8, "Tottenham": 0.7, "Newcastle": 0.6, "Brighton": 0.6,
        "Aston Villa": 0.65, "West Ham": 0.6, "Leicester": 0.5, "Brentford": 0.5,
        "Fulham": 0.4, "Crystal Palace": 0.5, "Wolves": 0.5, "Everton": 0.4,
        "Southampton": 0.4, "Bournemouth": 0.3, "Leeds": 0.3, "Burnley": 0.3,
        "Watford": 0.2, "Sheffield United": 0.2, "Norwich": 0.2,
        "Luton": 0.2, "Ipswich": 0.2, "Sunderland": 0.2, "Hull": 0.2
    }
    return stability_map.get(team, 0.5)

def predict_league_standings(team_stats_df, season_index=0, recent_champions=None):
    """
    Predicts league rankings based on team stats using a trained ML model,
    with additional realism and variability to prevent the same winners.
    
    Args:
        team_stats_df: DataFrame with team statistics
        season_index: Index of the season (0 for first, 1 for second, etc.)
            Used to increase variance over time
        recent_champions: List of teams that have won in recent seasons
            
    Returns:
        DataFrame sorted by predicted rank with realistic points
    """
    recent_champions = recent_champions or []
    
    # Create a copy to avoid modifying the original
    df = team_stats_df.copy()
    
    # Add any missing features needed by the model
    df = add_missing_features(df, season_index)
    
    df["MomentumScore"] = df["AvgPoints3Yrs"] * 0.6 + (100 - df["PrevRank"]) * 0.4

    feature_names = [
        "GF", "GA", "GD", "Win", "Draw", "Loss", "PromotedTeam",
        "ManagerRating", "TierScore", "RelegationRisk", "AvgPoints3Yrs",
        "PrevRank", "SquadAge", "SquadValue", "Injuries", "CleanSheets",
        "ShotsPerGame", "Possession", "PassAccuracy", "MomentumScore"
    ]

    # Ensure all required features exist
    for feature in feature_names:
        if feature not in df.columns:
            print(f"Adding missing feature: {feature}")
            if feature == "AvgPoints3Yrs":
                df[feature] = df["Points"] * 0.95  # Approximate as 95% of current points
            elif feature == "PrevRank":
                df[feature] = df["Points"].rank(ascending=False)  # Use current rank as placeholder
            else:
                df[feature] = 0  # Generic default
    
    # Select only the needed features
    X = df[feature_names].copy()

    # Scale features
    try:
        X_scaled = scaler.transform(X)
    except ValueError as e:
        print("Feature mismatch during scaling:", str(e))
        return df
    
    # Get base predictions from model
    base_predictions = model.predict(X_scaled) * 0.7 + (df["MomentumScore"] / 100) * 0.3
    
    # Add the predictions to the dataframe
    df["BasePoints"] = base_predictions
    
    df["BasePoints"] = df.apply(
        lambda row: apply_champion_penalty(row["Team"], row["BasePoints"], recent_champions),
        axis=1
    )
    
    # Apply realistic variance to prevent the same team always winning
    df["Points"] = df.apply(
        lambda row: apply_realistic_variance(
            row["Team"],
            row["BasePoints"],
            season_index
        ),
        axis=1
    )

    # Implement dynamic tier reassignment
    def reassign_team_tiers():
        sorted_teams = df.sort_values("Points", ascending=False)["Team"].tolist()
        TOP_TEAMS[:] = sorted_teams[:6]
        UPPER_MID_TEAMS[:] = sorted_teams[6:10]
        MID_TEAMS[:] = sorted_teams[10:14]
        LOWER_TEAMS[:] = sorted_teams[14:18]
        RELEGATION_CANDIDATES[:] = sorted_teams[18:]

    reassign_team_tiers()
    
    # Apply stronger fatigue penalty to recent champions
    for team in df["Team"]:
        count = recent_champions.count(team)
        if count >= 1:
            fatigue_penalty = 1 - (0.07 * count)  # Increase penalty to 7% per repeat
            df.loc[df["Team"] == team, "Points"] *= fatigue_penalty
    
    # Sort by points and assign ranks
    df = df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    df["PredictedRank"] = df.index + 1

    # Predict likely winner using winner model
    try:
        top_features = ["GF", "GA", "GD", "Win", "Draw", "Loss", "SquadValue", "SquadAge", "MomentumScore"]
        for feature in top_features:
            if feature not in df.columns:
                df[feature] = 0.0

        winner_X = df[top_features].copy()
        winner_index = winner_model.predict(winner_X).argmax()
        predicted_champion = df.iloc[winner_index]["Team"]
        df["PredictedChampion"] = predicted_champion
    except Exception as e:
        print("Winner model prediction failed:", str(e))
        df["PredictedChampion"] = None

    # Promote one random top 4 team if the same team keeps winning
    if season_index >= 3 and df["Team"].iloc[0] in recent_champions:
        candidates = df.iloc[1:4][~df.iloc[1:4]["Team"].isin(recent_champions)]
        if not candidates.empty:
            lucky = candidates.sample(1).index[0]
            df.at[lucky, "Points"] += np.random.uniform(4, 7)

    # Ensure realistic win/draw/loss counts that add up to 38 matches
    df = calculate_match_results(df)
    
    # Calculate goal difference if not already present
    if "GD" not in df.columns and "GF" in df.columns and "GA" in df.columns:
        df["GD"] = df["GF"] - df["GA"]
    
    df["PredictedChampion"] = predicted_champion if 'predicted_champion' in locals() else None
    
    return df

def calculate_match_results(df):
    """
    Calculate realistic win/draw/loss counts that add up to 38 matches
    and align with the predicted points
    """
    for idx, row in df.iterrows():
        points = row["Points"]
        
        # Estimate wins (3 points each)
        wins = int(points * 0.75 / 3)  # Approximately 75% of points from wins
        
        # Estimate draws (1 point each)
        draws = int(points * 0.25)  # Approximately 25% of points from draws
        
        # Adjust to match points exactly
        target_points = points
        current_points = wins * 3 + draws
        
        while current_points != target_points:
            if current_points < target_points:
                if target_points - current_points >= 3 and wins + draws < 38:
                    wins += 1
                    current_points += 3
                elif target_points - current_points >= 1 and wins + draws < 38:
                    draws += 1
                    current_points += 1
                else:
                    break  # Can't match exactly
            else:  # current_points > target_points
                if current_points - target_points >= 3 and wins > 0:
                    wins -= 1
                    current_points -= 3
                elif current_points - target_points >= 1 and draws > 0:
                    draws -= 1
                    current_points -= 1
                else:
                    break  # Can't match exactly
        
        # Calculate losses
        losses = 38 - wins - draws
        
        # Update the dataframe
        df.at[idx, "Win"] = wins
        df.at[idx, "Draw"] = draws
        df.at[idx, "Loss"] = losses
    
    return df