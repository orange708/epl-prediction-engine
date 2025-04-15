import pandas as pd
from src.core import Team

def load_team_stats(csv_path, season):
    df = pd.read_csv(csv_path)

    # Filter to one season
    df = df[df['Season'] == season]

    # Normalize ratings (based on Points for now)
    max_points = df['Points'].max()
    df['Rating'] = df['Points'] / max_points

    teams = []
    for _, row in df.iterrows():
        team = Team(
            name=row['Team'],
            rating=row['Rating'],
            season=row['Season']
        )
        teams.append(team)
    return teams