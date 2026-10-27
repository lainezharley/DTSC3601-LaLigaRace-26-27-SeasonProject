# Documentation

Detailed reference for every major function in the pipeline, in the order
they run. For setup and a quick example, see the [README](../README.md).

---

## `ingest.py` — data ingestion

### `fetch_season(season)`
Fetches all matches for one La Liga season from the football-data.org API.

| Arg | Type | Description |
|---|---|---|
| `season` | `int` | Season start year, e.g. `2025` for the 2025/26 season. |

**Returns:** `dict \| None` — the raw JSON response (with a `"matches"` list) on success, or `None` if the request failed.

**Side effects:** writes the raw response to `data/raw/season_<season>.json`.

### `store_matches(data, conn)`
Writes one season's matches into the local `matches` SQLite table, creating the table on first call.

| Arg | Type | Description |
|---|---|---|
| `data` | `dict` | Raw JSON from `fetch_season()`. |
| `conn` | `sqlite3.Connection` | Open connection to `data/la_liga.db`. |

Uses `INSERT OR REPLACE`, so re-running ingestion later safely updates existing rows (e.g. a match moving from `SCHEDULED` to `FINISHED` with a final score) instead of erroring or duplicating.

**`matches` table schema:**

| Column | Type | Description |
|---|---|---|
| `match_id` | INTEGER (PK) | Unique match ID from the API |
| `matchday` | INTEGER | La Liga matchday number |
| `utc_date` | TEXT | Kickoff time, UTC |
| `home_team` / `away_team` | TEXT | Team names |
| `home_score` / `away_score` | INTEGER | Final score (null if not yet played) |
| `status` | TEXT | e.g. `FINISHED`, `SCHEDULED` |

---

## `features.py` — feature engineering

All feature functions take a `before_date` argument and only look at matches strictly before it. This is intentional and important: it's what guarantees the model is only ever trained on information that would genuinely have been available before kickoff, with no lookahead into the future.

### `load_matches()`
Loads all `FINISHED` matches from the database, sorted oldest-first, with dates parsed as real datetimes.
**Returns:** `pandas.DataFrame`

### `result_label(row)`
Converts a match's score into a result label.
**Returns:** `"H"` (home win), `"A"` (away win), or `"D"` (draw).

### `team_recent_form(df, team, before_date, n=5)`
Points earned by `team` in its last `n` matches before `before_date` (3 for a win, 1 for a draw, 0 for a loss).
**Returns:** `int`, 0-15 for the default `n=5`.

### `team_goal_diff(df, team, before_date, n=5)`
Average goal difference for `team` over its last `n` matches — a smoother companion to form (distinguishes a team barely winning from one winning big).
**Returns:** `float`, `0.0` if the team has no prior matches on record.

### `rest_days(df, team, before_date)`
Days since `team`'s previous match — a proxy for fatigue/fixture congestion.
**Returns:** `int`, defaults to `7` if there's no prior match (e.g. the team's first match in the dataset).

### `build_features()`
Runs all of the above for every finished match and writes the result to `data/features.csv`. This is the table `train_model.py` trains on.

**Output columns:** `match_id, date, home_team, away_team, home_form, away_form, home_gd, away_gd, home_rest, away_rest, result`

---

## `train_model.py` — model training

### `train(features_path="data/features.csv", model_path="data/match_outcome_model.joblib", verbose=True)`
Trains the match-outcome classifier.

| Arg | Type | Description |
|---|---|---|
| `features_path` | `str` | CSV produced by `build_features()`. |
| `model_path` | `str` | Where to save the trained model. |
| `verbose` | `bool` | Print accuracy/classification report if `True`. |

**Model:** `sklearn.ensemble.RandomForestClassifier` (200 trees). Chosen because it handles non-linear feature interactions (e.g. "high form only matters when rest is also decent") reasonably well without much tuning, a good fit for a first-pass model.

**Train/test split:** 80/20, stratified by result so both splits keep a similar Home/Draw/Away ratio. Accuracy is reported on the held-out 20% the model never trained on.

**Returns:** the trained `RandomForestClassifier`.

---

## `predict_demo.py` — predictions

### `predict_matchup(model, home_form, away_form, home_gd, away_gd, home_rest, away_rest)`
Predicts outcome probabilities for one hypothetical matchup.

| Arg | Type | Description |
|---|---|---|
| `model` | classifier | A model from `train()`. |
| `home_form`, `away_form` | `int` | Points in last 5 matches (0-15). |
| `home_gd`, `away_gd` | `float` | Average goal difference, last 5 matches. |
| `home_rest`, `away_rest` | `int` | Days since each team's last match. |

**Returns:** `dict` — `{"Home win": prob, "Draw": prob, "Away win": prob}`, probabilities sum to `1.0`.

Uses `model.predict_proba()` rather than `model.predict()` deliberately — the project needs a full probability distribution per match (not just the single most likely outcome), since those probabilities are what will feed the season-long Monte Carlo simulation used to produce each team's title odds.

---

## What's next

The current pipeline covers ingestion through single-match prediction. Still to build: the Monte Carlo season simulator that converts these match probabilities into a title-winner probability per team, and the AWS deployment (S3, SageMaker, Lambda/ECS, CloudWatch) described in the README.
