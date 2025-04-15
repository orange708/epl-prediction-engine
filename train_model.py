import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Load data
df = pd.read_csv("data/processed/team_season_stats.csv")

# Sort by team and season to calculate rolling stats
df["SeasonOrder"] = df["Season"].apply(lambda s: int(s.split("/")[0]))
df = df.sort_values(by=["Team", "SeasonOrder"])

# Create target: Final league rank (lower = better)
df["FinalRank"] = df.groupby("Season")["Points"].rank(ascending=False, method="first")

# Calculate rolling average points (last 3 seasons)
df["AvgPoints3Yrs"] = df.groupby("Team")["Points"].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).mean())

# Calculate previous season rank
df["PrevRank"] = df.groupby("Team")["FinalRank"].shift(1)

df["PrevRank"].fillna(df["FinalRank"].mean(), inplace=True)  # fallback
df["AvgPoints3Yrs"].fillna(df["Points"].mean(), inplace=True)

# Flag promoted teams
promoted_teams = {
    "2014/2015": ["Leicester", "Burnley", "QPR"],
    "2015/2016": ["Watford", "Norwich", "Bournemouth"],
    "2016/2017": ["Burnley", "Middlesbrough", "Hull"],
    "2017/2018": ["Newcastle", "Brighton", "Huddersfield"],
    "2018/2019": ["Wolves", "Fulham", "Cardiff"],
    "2019/2020": ["Norwich", "Sheffield United", "Aston Villa"],
    "2020/2021": ["Leeds", "West Brom", "Fulham"],
    "2021/2022": ["Brentford", "Norwich", "Watford"],
    "2022/2023": ["Fulham", "Bournemouth", "Nott'm Forest"],
    "2023/2024": ["Burnley", "Sheffield United", "Luton"],
    "2024/2025": ["Sunderland", "Ipswich", "Leeds"]
}

df["PromotedTeam"] = df.apply(lambda row: 1 if row["Team"] in promoted_teams.get(row["Season"], []) else 0, axis=1)

# Estimate manager rating
top_teams = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
df["ManagerRating"] = df["Team"].apply(lambda t: 0.85 if t in top_teams else 0.65)

# Add TierScore based on team strength
df["TierScore"] = df["Team"].apply(lambda t: 3 if t in top_teams else (1 if df.loc[df["Team"] == t, "PromotedTeam"].iloc[0] == 1 else 2))

# Add RelegationRisk = inverse of Points normalized
df["RelegationRisk"] = df["Points"].max() - df["Points"]

# Features to use for prediction
features = [
    "Points", "GF", "GA", "GD", "Win", "Draw", "Loss", "PromotedTeam",
    "ManagerRating", "TierScore", "RelegationRisk", "AvgPoints3Yrs", "PrevRank"
]
X = df[features]
y = df["Points"]

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluate
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error (Points): {mae:.2f}")

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/final_points_model.pkl")
print("Model saved to models/final_points_model.pkl")

# Save scaler
joblib.dump(scaler, "models/final_points_scaler.pkl")
print("Scaler saved to models/final_points_scaler.pkl")