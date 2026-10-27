"""
PREDICTION DEMO
Loads the trained model and shows its output on an example matchup —
this is the part to show on screen for "predictions when receiving
ideal data."

Feel free to edit the numbers below to a real matchup by pulling a
team's actual recent form/goal-diff/rest values from data/features.csv.

Run:
  python predict_demo.py
"""
import joblib
import pandas as pd

FEATURES = ["home_form", "away_form", "home_gd", "away_gd", "home_rest", "away_rest"]


def predict_matchup(model, home_form, away_form, home_gd, away_gd, home_rest, away_rest):
    """Predict Home/Draw/Away probabilities for one hypothetical matchup.

    Args:
        model: A trained classifier from train_model.train(), with the
            same FEATURES used at training time.
        home_form, away_form (int): Points earned in each team's last 5
            matches (0-15).
        home_gd, away_gd (float): Average goal difference, last 5 matches.
        home_rest, away_rest (int): Days since each team's last match.

    Returns:
        dict: {"Home win": prob, "Draw": prob, "Away win": prob}, summing to 1.0.
    """
    example = pd.DataFrame([{
        "home_form": home_form, "away_form": away_form,
        "home_gd": home_gd, "away_gd": away_gd,
        "home_rest": home_rest, "away_rest": away_rest,
    }])[FEATURES]
    probs = model.predict_proba(example)[0]
    labels = {"H": "Home win", "D": "Draw", "A": "Away win"}
    return {labels[cls]: p for cls, p in zip(model.classes_, probs)}


if __name__ == "__main__":
    model = joblib.load("data/match_outcome_model.joblib")

    # Example: strong, in-form home team vs. a weaker, out-of-form away team
    result = predict_matchup(
        model,
        home_form=13,   # e.g. won 4, drew 1 of last 5 (max 15)
        away_form=4,    # e.g. mostly losses
        home_gd=1.8,    # avg goal difference, last 5 matches
        away_gd=-1.2,
        home_rest=6,    # days since last match
        away_rest=4,
    )

    print("Example matchup: strong home team (in form) vs weaker away team")
    print("Predicted probabilities:")
    for label, p in result.items():
        print(f"  {label}: {p:.1%}")
