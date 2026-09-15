# DTSC-3601 PremierLeague 26/27 Season Project
This is a semester project for my DTSC3601 - Predictive Analytics &amp; Their Implications course. The Premier League season runs from August - May, this will be a consistently updated project. Even past the course's semester the plan is to track the progress of the predicted winner &amp; placement changes as i'd like to compare the certainty of the model.

## Project Proposal:

# La Liga Title Race Predictor

**Studio 3 — Semester Project**
Team: Harley Lainez Murillo, Joshua Adeleke, Malamin Drammeh

## Overview

A live, self-updating serverless AI pipeline that tracks La Liga title odds throughout the 2026-2027 season. The system:

1. Predicts the outcome (Win/Draw/Loss) of upcoming La Liga fixtures using a trained ML model.
2. Feeds those probabilities into a Monte Carlo simulation of the remaining season to produce a title-winner probability per team (e.g. "Barcelona 34%, Real Madrid 29%, Atlético Madrid 18%..").
3. Automatically retrains and re-predicts after every matchday, so odds update in real time as results come in.

This methodology mirrors established approaches like FiveThirtyEight's Soccer Power Index (SPI): a match-outcome model paired with season simulation.

## Why This Project

La Liga started in August 2026, giving us a full season of fresh, real data from day one. It's one clean, continuously-updating prediction task rather than several disconnected models, which makes the course's monitoring and auto-retraining requirements meaningful instead of bolted on.

## What We're Predicting

- **Core model output:** Win/Draw/Loss probability for each upcoming fixture.
- **Derived output:** Simulated title-winner probability per team, updated weekly.
- **Stretch goal (time permitting):** Predicted final table order.

## Data Sources

Candidate APIs under comparison (on La Liga coverage, historical data availability, and free-tier rate limits):

- [API-Football (via RapidAPI)](https://rapidapi.com/GiulianoCrescimbeni/api/football98)
- [Football-data.org](https://www.football-data.org/)
- [SportsScore](https://sportscore.com/developers/)

Features planned: team form, goal difference, home/away splits, rest days between matches, head-to-head history.

## Architecture (AWS)

| Stage | Service | Purpose |
|---|---|---|
| Ingestion | Lambda + EventBridge (scheduled) | Pulls fresh match data after each matchday into S3 |
| Storage | S3 | `raw/`, `processed/`, and `predictions/title-odds/` |
| Feature processing | Lambda | Cleans data, builds features, logs data-quality issues |
| Training | SageMaker | Trains the match-outcome classifier (logistic regression or XGBoost) |
| Simulation | ECS/Fargate (batch job) | Runs the Monte Carlo season simulation |
| Serving | SageMaker endpoint or Lambda + API Gateway | Exposes current title odds + next-matchday predictions |
| Monitoring | CloudWatch | Tracks accuracy (log-loss/Brier score), data freshness, sanity checks |

## Rough Timeline

1. **Weeks 1–2:** Exploration — pick data API, get raw ingestion into S3 working, define target variable.
2. **Weeks 3–4:** Feature engineering + baseline model, get comfortable with SageMaker.
3. **Weeks 5–6:** Automate training as a SageMaker job, stand up the prediction API.
4. **Weeks 7–8:** Build CloudWatch monitoring + alerting rules.
5. **Weeks 9–10:** Automate the retraining loop (EventBridge-triggered); start documentation.
6. **Week 11:** Initial demo finished.
7. **Weeks 12+:** Polish, monitoring refinement, presentation prep.

## Risks & Mitigations

- **AWS learning curve** (team is new to AWS) — work through guided examples before building pipeline components.
- **API rate limits** on free tiers — compare shortlisted APIs early and design ingestion cadence around real limits.
- **Retraining cadence tied to a real, uneven match schedule** — trigger retraining off actual matchday completions, not a fixed timer.
- **Mid-season data/schema changes or accuracy drift** — CloudWatch monitoring and alerting designed to catch this early.
