"""
MODEL TRAINING
Trains the match-outcome classifier: given pre-match features, predict
Home win / Draw / Away win, plus a probability for each class.

Run:
  python train_model.py
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

FEATURES = ["home_form", "away_form", "home_gd", "away_gd", "home_rest", "away_rest"]


def train(features_path="data/features.csv", model_path="data/match_outcome_model.joblib", verbose=True):
    """Train the Random Forest match-outcome classifier and save it.

    Splits the feature table 80/20 (stratified by result, so each split
    keeps a similar H/D/A ratio), trains on the 80%, and reports accuracy
    on the held-out 20% so the number reflects matches the model never
    saw during training.

    Args:
        features_path (str): CSV produced by features.py.
        model_path (str): Where to save the trained model (joblib format).
        verbose (bool): Print accuracy/classification report if True.

    Returns:
        sklearn.ensemble.RandomForestClassifier: The trained model.
    """
    df = pd.read_csv(features_path)
    X = df[FEATURES]
    y = df["result"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    if verbose:
        preds = model.predict(X_test)
        print("Test accuracy:", round(accuracy_score(y_test, preds), 3))
        print(classification_report(y_test, preds))

    joblib.dump(model, model_path)
    if verbose:
        print(f"Model saved -> {model_path}")

    return model


if __name__ == "__main__":
    train()
