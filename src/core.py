import random

class Team:
    def __init__(self, name, rating, season, budget=100, manager_rating=0.5):
        self.name = name
        self.season = season
        self.rating = rating
        self.budget = budget
        self.manager_rating = manager_rating
        self.form = 0.5
        self.history = {}

    def evolve(self):
        # Allow rating to slightly increase or decrease to simulate realism
        self.rating *= random.uniform(0.97, 1.03)
        self.budget *= random.uniform(0.95, 1.1)
        self.form = 0.5

    def __repr__(self):
        return f"{self.name} ({self.season})"

class LeagueSimulator:
    def __init__(self, teams):
        self.teams = teams

    def simulate_season(self):
        results = []
        for team in self.teams:
            # Add more randomness to make the league more dynamic
            score = team.rating * random.uniform(0.9, 1.1) + team.manager_rating + random.gauss(0, 0.2)
            results.append((team, score))
        standings = sorted(results, key=lambda x: x[1], reverse=True)
        return [team for team, _ in standings]

    def simulate_multiple_seasons(self, num_years=5):
        history = {}
        for year in range(num_years):
            standings = self.simulate_season()
            season_year = f"Year {year + 1}"
            history[season_year] = [team.name for team in standings]
            for team in self.teams:
                team.evolve()
                team.season = season_year
        return history