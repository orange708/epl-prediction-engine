import requests
import pandas as pd
import os
import time

API_KEY = "b74d8f5aae6213568229f575ed7e0ede"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

SEASON = "2024"
LEAGUE_ID = 39  # Premier League

def fetch_teams():
    url = f"{BASE_URL}/teams?league={LEAGUE_ID}&season={SEASON}"
    res = requests.get(url, headers=HEADERS)
    data = res.json().get("response", [])
    teams = {team["team"]["id"]: team["team"]["name"] for team in data}
    return teams

def fetch_squad(team_id):
    url = f"{BASE_URL}/players?team={team_id}&season={SEASON}"
    players = []
    page = 1

    while True:
        res = requests.get(url + f"&page={page}", headers=HEADERS)
        time.sleep(1)  # Avoid rate limits
        d = res.json().get("response", [])
        if not d:
            break
        players.extend(d)
        page += 1

    return players

def fetch_transfers(team_id):
    url = f"{BASE_URL}/transfers?team={team_id}"
    res = requests.get(url, headers=HEADERS)
    return res.json().get("response", [])

def main():
    os.makedirs("data/raw/squads", exist_ok=True)
    os.makedirs("data/raw/transfers", exist_ok=True)
    os.makedirs("data/processed/squads", exist_ok=True)
    os.makedirs("data/processed/transfers", exist_ok=True)

    teams = fetch_teams()

    for team_id, name in teams.items():
        print(f"Fetching data for {name}...")

        squad_raw = fetch_squad(team_id)
        transfer_raw = fetch_transfers(team_id)

        # Save raw
        pd.DataFrame(squad_raw).to_json(f"data/raw/squads/{name}.json", orient="records", indent=2)
        pd.DataFrame(transfer_raw).to_json(f"data/raw/transfers/{name}.json", orient="records", indent=2)

        # Process squad
        squad_processed = []
        for entry in squad_raw:
            player = entry["player"]
            stats = entry["statistics"][0] if entry["statistics"] else {}
            squad_processed.append({
                "Name": player.get("name"),
                "Age": player.get("age"),
                "Nationality": player.get("nationality"),
                "Position": stats.get("games", {}).get("position"),
                "Appearances": stats.get("games", {}).get("appearences", 0),
                "Goals": stats.get("goals", {}).get("total", 0),
                "Assists": stats.get("goals", {}).get("assists", 0),
                "Minutes": stats.get("games", {}).get("minutes", 0)
            })

        pd.DataFrame(squad_processed).to_csv(f"data/processed/squads/{name}.csv", index=False)

        # Process transfers
        transfers_processed = []
        for t in transfer_raw:
            player = t["player"]
            transfers_processed.append({
                "Name": player.get("name"),
                "Type": t.get("type"),
                "From": t["teams"].get("out", {}).get("name"),
                "To": t["teams"].get("in", {}).get("name"),
                "Date": t.get("date")
            })

        pd.DataFrame(transfers_processed).to_csv(f"data/processed/transfers/{name}.csv", index=False)

    print("✅ Processed squad and transfer data saved.")

if __name__ == "__main__":
    main()
