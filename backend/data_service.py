import pandas as pd
import numpy as np
import random
from typing import Dict, List, Optional, Any

class DataService:
    """Service responsible for team data operations and predictions"""
    
    def __init__(self, data_path: str = "data/processed/simulated_season_history.csv"):
        """Initialize with the path to simulation data"""
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        self.seasons = sorted(self.df["Season"].unique())
        
    def get_standings(self, season: str) -> List[Dict[str, Any]]:
        """Get league standings for a specific season"""
        if season not in self.seasons:
            # If season not found, return most recent season
            season = self.seasons[-1]
        
        standings = self.df[self.df["Season"] == season].copy()
        
        # Calculate match stats if they don't exist
        if "Matches" not in standings.columns:
            standings["Matches"] = 38
        
        # Ensure Win/Draw/Loss columns exist
        if "Win" not in standings.columns or "Draw" not in standings.columns or "Loss" not in standings.columns:
            # Approximate wins and draws based on points
            standings["Win"] = (standings["Points"] * 0.8 / 3).round().astype(int)
            standings["Draw"] = (standings["Points"] * 0.2 / 1).round().astype(int) 
            standings["Loss"] = standings["Matches"] - standings["Win"] - standings["Draw"]
        
        # Sort by points in descending order
        standings = standings.sort_values(by=["Points"], ascending=False)
        
        # Add predicted rank if missing
        if "PredictedRank" not in standings.columns:
            standings["PredictedRank"] = standings.index + 1
            
        # Prepare the data for JSON serialization
        return standings[["Team", "Points", "Matches", "Win", "Draw", "Loss", "PredictedRank"]].to_dict(orient="records")
    
    def get_team_details(self, season: str, team: str) -> Dict[str, Any]:
        """Get detailed stats for a specific team in a specific season"""
        if season not in self.seasons:
            season = self.seasons[-1]
            
        team_data = self.df[(self.df["Season"] == season) & (self.df["Team"] == team)]
        
        if team_data.empty:
            # If team not found, return empty data with status
            return {
                "team": team,
                "season": season,
                "error": "Team not found in this season"
            }
        
        # Get the team data as a dictionary
        data = team_data.iloc[0].to_dict()
        
        # Add additional metrics if they don't exist
        if "winRate" not in data and "Win" in data and "Matches" in data:
            data["winRate"] = round((data["Win"] / data["Matches"]) * 100)
            
        if "cleanSheets" not in data:
            # Estimate clean sheets based on goals against
            if "GA" in data:
                data["cleanSheets"] = max(1, round(38 - (data["GA"] / 2)))
            else:
                data["cleanSheets"] = random.randint(5, 15)
                
        if "possession" not in data:
            # Estimate possession based on team quality
            if "TierScore" in data:
                base = 45 + (data["TierScore"] * 5)
                data["possession"] = min(65, max(35, round(base + random.uniform(-5, 5))))
            else:
                data["possession"] = random.randint(45, 60)
        
        if "predictedRank" not in data and "PredictedRank" in data:
            data["predictedRank"] = data["PredictedRank"]
            
        # Rename some fields for frontend consistency
        if "GF" in data and "goalsScored" not in data:
            data["goalsScored"] = data["GF"]
            
        if "GA" in data and "goalsConceded" not in data:
            data["goalsConceded"] = data["GA"]
            
        if "AvgPoints3Yrs" in data and "avgPoints" not in data:
            data["avgPoints"] = data["AvgPoints3Yrs"]
        
        # Convert relegation risk to text
        if "RelegationRisk" in data and "relegationRisk" not in data:
            risk_value = data["RelegationRisk"]
            if risk_value < 20:
                data["relegationRisk"] = "None"
            elif risk_value < 40:
                data["relegationRisk"] = "Low"
            elif risk_value < 60:
                data["relegationRisk"] = "Medium"
            else:
                data["relegationRisk"] = "High"
                
        return data