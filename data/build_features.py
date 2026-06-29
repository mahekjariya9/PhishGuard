# build_features.py
# Runs feature extraction on every URL in urls_raw.csv and writes
# the numeric feature matrix to features.csv.

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from feature_extraction import extract_features, FEATURE_NAMES

df = pd.read_csv(BASE_DIR / "data" / "urls_raw.csv")

feature_rows = [extract_features(url) for url in df["url"]]
features_df = pd.DataFrame(feature_rows, columns=FEATURE_NAMES)
features_df["label"] = df["label"].values
features_df["url"] = df["url"].values

features_df.to_csv(BASE_DIR / "data" / "features.csv", index=False)
print(f"Built feature matrix: {features_df.shape[0]} rows x {len(FEATURE_NAMES)} features")
print(features_df.drop(columns=["url"]).describe().T[["mean", "std", "min", "max"]])
