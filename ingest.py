"""
INGESTION
Pulls La Liga match data from football-data.org and stores it locally.

Tonight this saves to a local SQLite file as a stand-in for S3 — in the
real AWS pipeline, this same logic runs in a Lambda and writes to S3
(raw/) on a schedule (EventBridge) after every matchday.

Setup:
  1. Get a free API key: https://www.football-data.org/client/register
     (instant, no credit card)
  2. Paste it into API_KEY below.
  3. pip install -r requirements.txt
  4. python ingest.py
"""
import requests
import json
import os
import sqlite3

API_KEY = "PASTE_YOUR_FREE_API_KEY_HERE"
BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "PD"  # La Liga (Primera Division) competition code
SEASONS = [2022, 2023, 2024, 2025, 2026]  # past seasons for training + current season

RAW_DIR = "data/raw"
DB_PATH = "data/la_liga.db"


def fetch_season(season):
    """Fetch all matches for one La Liga season from football-data.org.

    Args:
        season (int): Season start year, e.g. 2025 for the 2025/26 season.

    Returns:
        dict | None: The raw JSON response (contains a "matches" list) on
        success, or None if the request failed (e.g. invalid key, season
        not covered by the current API plan).

    Side effects:
        Writes the raw JSON response to data/raw/season_<season>.json.
    """
    url = f"{BASE_URL}/competitions/{COMPETITION}/matches"
    headers = {"X-Auth-Token": API_KEY}
    params = {"season": season}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"Season {season}: request failed ({resp.status_code}) - skipping")
        print(f"  API response: {resp.text}")
        return None
    data = resp.json()
    raw_path = os.path.join(RAW_DIR, f"season_{season}.json")
    with open(raw_path, "w") as f:
        json.dump(data, f)
    print(f"Season {season}: saved {len(data.get('matches', []))} matches -> {raw_path}")
    return data


def store_matches(data, conn):
    """Write one season's matches into the local `matches` table.

    Creates the table on first call. Uses INSERT OR REPLACE so re-running
    ingestion later (e.g. after more matches finish) safely updates rows
    instead of duplicating or erroring.

    Args:
        data (dict): Raw JSON response from fetch_season(), containing a
            "matches" list.
        conn (sqlite3.Connection): Open connection to the local database.
    """
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            matchday INTEGER,
            utc_date TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            status TEXT
        )
    """)
    for m in data.get("matches", []):
        score = m.get("score", {}).get("fullTime", {})
        cur.execute("""
            INSERT OR REPLACE INTO matches
            (match_id, matchday, utc_date, home_team, away_team, home_score, away_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["id"],
            m.get("matchday"),
            m.get("utcDate"),
            m["homeTeam"]["name"],
            m["awayTeam"]["name"],
            score.get("home"),
            score.get("away"),
            m.get("status"),
        ))
    conn.commit()


if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    total = 0
    for season in SEASONS:
        data = fetch_season(season)
        if data:
            store_matches(data, conn)
            total += len(data.get("matches", []))
    conn.close()
    print(f"\nDone. {total} matches stored locally at {DB_PATH}")
