# La Liga Title Race Predictor

**DTSC 3601 — Data Science Studio 3 | Team: Goop Troop**
Harley Lainez Murillo, Joshua Adeleke, Malamin Drammeh

A weekly-updated tool that estimates each club's probability of winning the current La Liga season. Rather than a one-time preseason guess, it recalculates the odds after every matchday using a match-outcome classifier and a Monte Carlo season simulation.

> This repo is an extension of our Initial Documentation and Initial Demo submissions. Check [DOCUMENTATION.md](./DOCUMENTATION.md) for full function-level reference.

## How It Works

1. **Ingest** real match data from a football API.
2. **Engineer features** — each team's recent form, goal difference, and rest days, computed using only data available before that match (no lookahead).
3. **Train** a classifier that predicts Home win / Draw / Away win probabilities for a fixture.
4. *(In progress)* Feed those probabilities into a **Monte Carlo simulation** of the rest of the season to get a title probability per team.

## Installation

**Required libraries:**
- `requests`
- `pandas`
- `scikit-learn`
- `joblib`

**Install:**
```bash
git clone https://github.com/lainezharley/DTSC3601-LaLigaRace-26-27-SeasonProject.git
cd DTSC3601-LaLigaRace-26-27-SeasonProject
pip install -r requirements.txt
```

## Get Started (quick demo, no API key needed)

To see the full pipeline: train a model and get a prediction (in seconds), on a small synthetic dataset:
```bash
python bin/run_demo.py
```
This builds a small fake dataset, trains the classifier on it, and prints an example prediction. It's meant purely to let you see every stage run end to end before setting up real data below.

## Usage (full pipeline, real data)

1. Get a free API key at [football-data.org](https://www.football-data.org/client/register) (instant, no card required).
2. Paste it into `API_KEY` in `ingest.py`.
3. Run the pipeline in order:
```bash
python ingest.py          # pulls La Liga match data -> data/la_liga.db
python features.py        # builds model features -> data/features.csv
python train_model.py     # trains the classifier -> data/match_outcome_model.joblib
python predict_demo.py    # example prediction for a sample matchup
```

## Project Structure

```
.
├── ingest.py                # Pulls match data from the API, stores locally
├── features.py               # Builds pre-match features (form, goal diff, rest)
├── train_model.py            # Trains the Random Forest match-outcome classifier
├── predict_demo.py           # Example prediction on a sample matchup
├── bin/
│   └── run_demo.py           # Quick-start demo on synthetic data (no API key needed)
├── docs/
│   └── DOCUMENTATION.md      # Full function-level documentation
├── requirements.txt
└── LICENSE
```

## Data Source

Match, fixture, and team data from [football-data.org](https://www.football-data.org/) (free tier, La Liga competition code `PD`). We're still comparing it against [API-Football](https://rapidapi.com/GiulianoCrescimbeni/api/football98) and [SportsScore](https://sportscore.com/developers/) on coverage and rate limits.

## Model

The core model is a **classifier**, not a regression model. For a given fixture it outputs a probability for each of three classes — Home win, Draw, Away win. Current test accuracy is ~46% on this 3-class problem (vs. ~33% for random guessing). Check [DOCUMENTATION.md](./DOCUMENTATION.md) for details on each feature and function.

## Roadmap

- [ ] Monte Carlo season simulation to convert match probabilities into title odds
- [ ] Migrate pipeline to AWS (S3, SageMaker, Lambda/ECS, CloudWatch)
- [ ] Automate weekly retraining after each matchday
- [ ] Serve results through an API/dashboard

## License

[MIT](LICENSE)

## Contact

Questions? Reach out to:
- Harley Lainez Murillo - hlainezm@charlotte.edu
- Malamin Drammeh - mdramme2@charlotte.edu
- Joshua Adeleke jadelek3@charlotte.edu
