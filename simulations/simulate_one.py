import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.predictor import predict_league_standings

# Load team stats for all seasons
df_all = pd.read_csv("data/processed/team_season_stats.csv")
seasons = sorted(df_all["Season"].unique())

# Add FinalRank if missing
if "FinalRank" not in df_all.columns:
    df_all["FinalRank"] = df_all.groupby("Season")["Points"].rank(method="first", ascending=False).astype(int)

# Compute AvgPoints3Yrs
df_all["AvgPoints3Yrs"] = df_all.groupby("Team")["Points"].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

# Run prediction season by season
for season in seasons:
    df = df_all[df_all["Season"] == season].copy()

    # Add PromotedTeam flag (manually for now)
    promoted_teams = {
        "2013/2014": ["Crystal Palace", "Hull", "Cardiff"],
        "2014/2015": ["Leicester", "Burnley", "QPR"],
        "2015/2016": ["Bournemouth", "Watford", "Norwich"],
        "2016/2017": ["Burnley", "Middlesbrough", "Hull"],
        "2017/2018": ["Newcastle", "Brighton", "Huddersfield"],
        "2018/2019": ["Wolves", "Cardiff", "Fulham"],
        "2019/2020": ["Norwich", "Sheffield Utd", "Aston Villa"],
        "2020/2021": ["Leeds", "West Brom", "Fulham"],
        "2021/2022": ["Norwich", "Watford", "Brentford"],
        "2022/2023": ["Fulham", "Bournemouth", "Nott'm Forest"],
        "2023/2024": ["Burnley", "Sheffield Utd", "Luton"],
        "2024/2025": ["Sunderland", "Ipswich", "Leeds"]
    }
    df["PromotedTeam"] = df["Team"].apply(lambda t: 1 if t in promoted_teams.get(season, []) else 0)

    top_teams = ["Man City", "Liverpool", "Chelsea", "Arsenal", "Man United", "Tottenham"]
    df["ManagerRating"] = df["Team"].apply(lambda t: 0.85 if t in top_teams else 0.65)
    df["TierScore"] = df["Team"].apply(lambda t: 3 if t in top_teams else (1 if df[df["Team"] == t]["PromotedTeam"].iloc[0] == 1 else 2))
    df["RelegationRisk"] = df["Points"].max() - df["Points"]

    # Inject historical features
    prev_season_index = seasons.index(season) - 1
    if prev_season_index >= 0:
        prev_season = seasons[prev_season_index]
        prev_rank_map = df_all[df_all["Season"] == prev_season].set_index("Team")["FinalRank"].to_dict()
        df["PrevRank"] = df["Team"].map(prev_rank_map).fillna(21)
    else:
        df["PrevRank"] = 21

    avg_points_map = df_all[df_all["Season"] == season].set_index("Team")["AvgPoints3Yrs"].to_dict()
    df["AvgPoints3Yrs"] = df["Team"].map(avg_points_map).fillna(df["Points"].mean())

    # Add engineered features expected by the model
    df["FormFactor"] = df["Points"] / 38

    required_columns = {
        "CleanSheets": 10,
        "ShotsPerGame": 10,
        "Possession": 55,
        "PassAccuracy": 80,
        "SquadValue": 500,
        "SquadAge": 27,
        "Injuries": 5
    }
    for col, default in required_columns.items():
        if col not in df.columns:
            df[col] = default

    df["DefensiveStability"] = df["CleanSheets"] / 38
    df["AttackRating"] = df["GF"] / df["ShotsPerGame"]
    df["PassSuccess"] = df["Possession"] * df["PassAccuracy"]
    df["FormIndex"] = (df["Win"] - df["Loss"]) / 38
    df["SquadStrength"] = df["SquadValue"] / df["SquadAge"]
    df["InjuryImpact"] = df["Injuries"] / 38
    df["MomentumScore"] = df["FormIndex"] + df["FormFactor"]

    # Fill any missing values with mean of the column
    df.fillna(df.mean(numeric_only=True), inplace=True)

    predicted_table = predict_league_standings(df)

    print(f"\n🏆 Predicted Standings for {season}:")
    for i, team in enumerate(predicted_table["Team"], 1):
        print(f"{i}. {team}")