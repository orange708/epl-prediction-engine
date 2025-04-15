import random
import requests
import os

POSITIONS = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
NATIONALITIES = ["England", "France", "Germany", "Spain", "Brazil", "Netherlands", "Portugal", "Italy"]

def predict_future_squad(team: str, season: str):
    API_KEY = os.getenv("API_FOOTBALL_KEY") or "b74d8f5aae6213568229f575ed7e0ede"
    headers = {
        "x-apisports-key": API_KEY
    }

    # Get team ID
    team_search_url = f"https://v3.football.api-sports.io/teams?search={team}"
    search_response = requests.get(team_search_url, headers=headers)
    try:
        team_id = search_response.json()["response"][0]["team"]["id"]
    except (IndexError, KeyError):
        print(f"Error fetching team ID for {team}, using fallback squad.")
        return fallback_squad(team, season)

    current_year = 2023
    target_year = int(season[:4])
    year_diff = target_year - current_year

    # Get current squad from base year
    squad_url = f"https://v3.football.api-sports.io/players?team={team_id}&season=2023"
    squad_response = requests.get(squad_url, headers=headers)

    try:
        players_data = squad_response.json()["response"]
        squad = []

        retained = 0
        for player in players_data:
            info = player["player"]
            age = info["age"] + year_diff
            position = player["statistics"][0]["games"]["position"]
            if age <= 36 and retained < 8:
                squad.append({
                    "name": info["name"],
                    "position": position,
                    "age": age,
                    "nationality": info["nationality"],
                    "number": info.get("number", 0),
                    "photo": info.get("photo", "https://api.sportmonks.com/images/default-player.png")
                })
                retained += 1

        # Simulate 1-3 new signings per year of difference
        num_signings = max(0, 11 - len(squad))
        transfer_rumor_url = f"https://v3.football.api-sports.io/transfers?team={team_id}"
        rumor_response = requests.get(transfer_rumor_url, headers=headers)

        if rumor_response.status_code == 200:
            rumors = rumor_response.json().get("response", [])
            added = 0
            for rumor in rumors:
                if added >= num_signings:
                    break
                player_info = rumor.get("player", {})
                if not player_info:
                    continue
                new_player = {
                    "name": player_info.get("name", f"Future Signing {added+1}"),
                    "position": random.choice(POSITIONS),
                    "age": random.randint(20, 28),
                    "nationality": player_info.get("nationality", "England"),
                    "number": 0,
                    "photo": player_info.get("photo", "https://api.sportmonks.com/images/default-player.png")
                }
                squad.append(new_player)
                added += 1

        return squad

    except Exception as e:
        print("Error fetching squad or simulating transfers:", e)
        return fallback_squad(team, season)

def fallback_squad(team, season):
    POSITIONS = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
    NATIONALITIES = ["England", "France", "Germany", "Spain", "Brazil", "Netherlands", "Portugal", "Italy"]
    squad = []
    for i in range(11):
        player = {
            "name": f"{season} Player {i+1}",
            "position": random.choice(POSITIONS),
            "age": random.randint(20, 30) + 5,
            "nationality": random.choice(NATIONALITIES),
            "number": i + 1,
            "photo": "https://api.sportmonks.com/images/default-player.png"
        }
        squad.append(player)
    return squad
