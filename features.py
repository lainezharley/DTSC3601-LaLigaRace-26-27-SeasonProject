"""
FEATURE ENGINEERING
Builds the feature set the model trains on, from the raw match data
stored by ingest.py.

Features (each computed as of the match date, using only past data —
no lookahead):
  - home_form / away_form : points earned in each team's last 5 matches
  - home_gd / away_gd     : average goal difference over last 5 matches
  - home_rest / away_rest : days of rest since each team's last match

Run:
  python features.py
"""
import sqlite3
import pandas as pd

DB_PATH = "data/la_liga.db"


def load_matches():
    """Load all FINISHED matches from the local database, sorted by date.

    Returns:
        pandas.DataFrame: One row per finished match, sorted oldest-first,
        with utc_date parsed as a real datetime.
    """
    conn = sqlite3.connect(DB_PATH) # Open a connection to the SQLite database at the specified path.
    df = pd.read_sql("SELECT * FROM matches WHERE status = 'FINISHED'", conn) # Execute a SQL query to select all rows from the "matches" table where the status is 'FINISHED', and load the result into a pandas DataFrame.
    conn.close() # Close the database connection.
    df["utc_date"] = pd.to_datetime(df["utc_date"])
    return df.sort_values("utc_date").reset_index(drop=True)


def result_label(row): 
    """Return the match result from the home team's perspective.

    Args:
        row: A row with home_score and away_score columns.

    Returns:
        str: "H" (home win), "A" (away win), or "D" (draw).
    """
    if row["home_score"] > row["away_score"]:
        return "H"
    elif row["home_score"] < row["away_score"]:
        return "A"
    return "D"


def _team_history(df, team, before_date, n=5):
    """Internal helper: a team's last n matches strictly before a date.

    The `before_date` filter is what keeps every feature pre-match-only —
    it guarantees the model never sees information from the future.
    """
    past = df[((df["home_team"] == team) | (df["away_team"] == team)) & (df["utc_date"] < before_date)]
    return past.sort_values("utc_date").tail(n)


def team_recent_form(df, team, before_date, n=5):
    """Points earned by `team` in its last n matches before before_date.

    Standard football scoring: 3 points for a win, 1 for a draw, 0 for a
    loss. Used as a short-term "how well is this team playing right now"
    signal.

    Args:
        df: Full match history (from load_matches()).
        team (str): Team name as it appears in the data.
        before_date: Only matches strictly before this date count.
        n (int): Window size (default: last 5 matches).

    Returns:
        int: Points earned, 0-15 for n=5.
    """
    past = _team_history(df, team, before_date, n)
    pts = 0
    for _, m in past.iterrows():
        gf, ga = (m["home_score"], m["away_score"]) if m["home_team"] == team else (m["away_score"], m["home_score"])
        pts += 3 if gf > ga else (1 if gf == ga else 0)
    return pts


def team_goal_diff(df, team, before_date, n=5):
    """Average goal difference for `team` over its last n matches.

    A smoother complement to form: a team winning 1-0 every match and a
    team winning 4-0 every match get the same form score, but very
    different goal-difference scores.

    Returns:
        float: Average (goals for - goals against) over the window, 0.0
        if the team has no prior matches yet.
    """
    past = _team_history(df, team, before_date, n)
    if past.empty:
        return 0.0
    diffs = []
    for _, m in past.iterrows():
        diffs.append((m["home_score"] - m["away_score"]) if m["home_team"] == team
                      else (m["away_score"] - m["home_score"]))
    return sum(diffs) / len(diffs)


def rest_days(df, team, before_date):
    """Days since `team`'s previous match.

    Used as a proxy for fatigue / fixture congestion. Defaults to 7 (a
    normal weekly gap) when there's no prior match on record, e.g. the
    team's first game in our dataset.

    Returns:
        int: Days of rest before this match.
    """
    past = _team_history(df, team, before_date, n=1)
    if past.empty:
        return 7
    return (before_date - past["utc_date"].max()).days


def build_features():
    """Build the full feature table and write it to data/features.csv.

    For every finished match, computes home/away form, goal difference,
    and rest days as of that match's date, plus the actual result label.
    This is the table train_model.py trains on.

    Returns:
        pandas.DataFrame: The feature table (also saved to disk).
    """
    df = load_matches()
    rows = []
    for _, m in df.iterrows():
        rows.append({
            "match_id": m["match_id"],
            "date": m["utc_date"],
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "home_form": team_recent_form(df, m["home_team"], m["utc_date"]),
            "away_form": team_recent_form(df, m["away_team"], m["utc_date"]),
            "home_gd": team_goal_diff(df, m["home_team"], m["utc_date"]),
            "away_gd": team_goal_diff(df, m["away_team"], m["utc_date"]),
            "home_rest": rest_days(df, m["home_team"], m["utc_date"]),
            "away_rest": rest_days(df, m["away_team"], m["utc_date"]),
            "result": result_label(m),
        })
    feat_df = pd.DataFrame(rows)
    feat_df.to_csv("data/features.csv", index=False)
    print(f"Built {len(feat_df)} feature rows -> data/features.csv")
    print(feat_df.head())
    return feat_df


if __name__ == "__main__":
    build_features()
