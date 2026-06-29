# train_model.py
# Trains a Random Forest classifier on the URL feature set and saves
# the model, metrics, and evaluation plots.

import json
import pickle
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "features.csv"
MODEL_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "static"
MODEL_PATH = MODEL_DIR / "phishguard_model.pkl"
METRICS_PATH = MODEL_DIR / "metrics.json"


def main():
    MODEL_DIR.mkdir(exist_ok=True)
    STATIC_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=["label", "url"])
    y = df["label"]
    feature_names = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )

    # 5-fold cross-validation on the training set
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    print(f"Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    metrics = {
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores.std()), 4),
        "test_accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "test_precision": round(float(precision_score(y_test, y_pred)), 4),
        "test_recall": round(float(recall_score(y_test, y_pred)), 4),
        "test_f1": round(float(f1_score(y_test, y_pred)), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    print("\nTest set performance:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, target_names=["legitimate", "phishing"]))

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": clf, "feature_names": feature_names}, f)

    # --- Confusion matrix plot ---
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4.2))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["legitimate", "phishing"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["legitimate", "phishing"])
    ax.set_xlabel("Predicted label"); ax.set_ylabel("True label")
    ax.set_title("PhishGuard — confusion matrix")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=14)
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(STATIC_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    # --- Feature importance plot ---
    importances = clf.feature_importances_
    order = np.argsort(importances)[::-1]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh([feature_names[i] for i in order][::-1], importances[order][::-1], color="#1D9E75")
    ax.set_xlabel("Feature importance")
    ax.set_title("PhishGuard — feature importance (Random Forest)")
    fig.tight_layout()
    fig.savefig(STATIC_DIR / "feature_importance.png", dpi=150)
    plt.close(fig)

    print("\nSaved model ->", MODEL_PATH)
    print("Saved metrics ->", METRICS_PATH)
    print("Saved plots -> static/confusion_matrix.png, static/feature_importance.png")


if __name__ == "__main__":
    main()
