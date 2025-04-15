import requests

API_KEY = "b74d8f5aae6213568229f575ed7e0ede"
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

TEAM_ID_MAP = {
    "Arsenal": 42,
    "Aston Villa": 66,
    "Bournemouth": 35,
    "Brentford": 55,
    "Brighton": 51,
    "Burnley": 44,
    "Chelsea": 49,
    "Crystal Palace": 52,
    "Everton": 45,
    "Fulham": 36,
    "Leicester": 46,
    "Liverpool": 40,
    "Luton": 71,
    "Man City": 50,
    "Man United": 33,
    "Newcastle": 34,
    "Nott'm Forest": 65,
    "Sheffield United": 62,
    "Tottenham": 47,
    "West Ham": 48,
    "Wolves": 39
}

def get_team_transfers(team_id, season):
    url = f"{BASE_URL}/transfers?team={team_id}&season={season}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []