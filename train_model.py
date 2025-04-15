import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Load dataset
df = pd.read_csv("data/processed/team_season_stats.csv")

# Drop nulls for key columns
df = df.dropna(subset=["Points", "Team", "Season"])

# Season-based numeric sort
df["SeasonOrder"] = df["Season"].apply(lambda s: int(s.split("/")[0]))
df = df.sort_values(by=["Team", "SeasonOrder"])

# Final rank
df["FinalRank"] = df.groupby("Season")["Points"].rank(ascending=False, method="first")

# Rolling averages and previous rank
df["AvgPoints3Yrs"] = df.groupby("Team")["Points"].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).mean())
df["PrevRank"] = df.groupby("Team")["FinalRank"].shift(1)

df["PrevRank"] = df["PrevRank"].fillna(df["FinalRank"].mean())
df["AvgPoints3Yrs"] = df["AvgPoints3Yrs"].fillna(df["Points"].mean())

# Add new rolling features
df["AvgGD3Yrs"] = df.groupby("Team")["GD"].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).mean())
df["AvgGF3Yrs"] = df.groupby("Team")["GF"].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).mean())
df["AvgGA3Yrs"] = df.groupby("Team")["GA"].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).mean())

# Fill missing values
df["AvgGD3Yrs"] = df["AvgGD3Yrs"].fillna(df["GD"].mean())
df["AvgGF3Yrs"] = df["AvgGF3Yrs"].fillna(df["GF"].mean())
df["AvgGA3Yrs"] = df["AvgGA3Yrs"].fillna(df["GA"].mean())

# Advanced features
df["GoalEfficiency"] = df["GF"] / (df["GF"] + df["GA"])
df["WinRate"] = df["Win"] / (df["Win"] + df["Draw"] + df["Loss"])
df["FormFactor"] = df["Points"] / 38  # assuming 38 games per season
# Slight random noise to introduce variation and reduce model overfitting to history
np.random.seed(42)
df["RandomNoise"] = np.random.normal(0, 1, len(df))

# Promoted teams
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

# Manager rating and tier
top_teams = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
df["ManagerRating"] = df["Team"].apply(lambda t: 0.85 if t in top_teams else 0.65)
df["TierScore"] = df["Team"].apply(lambda t: 3 if t in top_teams else (1 if df.loc[df["Team"] == t, "PromotedTeam"].iloc[0] == 1 else 2))

# Relegation Risk
df["RelegationRisk"] = df["Points"].max() - df["Points"]

# Features and target
df["AvgPoints3Yrs"] = df["AvgPoints3Yrs"] * 0.75
features = [
    "GF", "GA", "GD", "Win", "Draw", "Loss", "PromotedTeam",
    "ManagerRating", "TierScore", "RelegationRisk", "AvgPoints3Yrs", "PrevRank",
    "GoalEfficiency", "WinRate", "FormFactor", "AvgGD3Yrs", "AvgGF3Yrs", "AvgGA3Yrs",
    "RandomNoise"
]
target = "Points"

X = df[features]
y = df[target]

# Normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train model
model = HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05, max_depth=6, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"R2 Score: {r2_score(y_test, y_pred):.2f}")

# Save
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/final_points_model.pkl")
joblib.dump(scaler, "models/final_points_scaler.pkl")
print("✅ Model and scaler saved.")