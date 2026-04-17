"""
Classical feature-selection methods (Step 1 of the two-step pipeline).

Techniques implemented:
  - XGBoost feature importance
  - Random Forest feature importance
  - Mutual Information
  - Chi-squared test (on shifted features ≥ 0)

Each method ranks features; the final ranking is an ensemble vote
that selects the top-K features appearing most often across methods.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import (
    mutual_info_classif,
    chi2,
    SelectKBest,
)
from xgboost import XGBClassifier

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def _xgb_importance(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> pd.Series:
    model = XGBClassifier(**config.XGBOOST_PARAMS)
    model.fit(X, y)
    imp = model.feature_importances_
    return pd.Series(imp, index=feature_names).sort_values(ascending=False)


def _rf_importance(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> pd.Series:
    model = RandomForestClassifier(**config.RF_PARAMS)
    model.fit(X, y)
    imp = model.feature_importances_
    return pd.Series(imp, index=feature_names).sort_values(ascending=False)


def _mutual_info(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> pd.Series:
    mi = mutual_info_classif(X, y, random_state=config.RANDOM_STATE)
    return pd.Series(mi, index=feature_names).sort_values(ascending=False)


def _chi_squared(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> pd.Series:
    X_shifted = X - X.min(axis=0)
    scores, _ = chi2(X_shifted, y)
    return pd.Series(scores, index=feature_names).sort_values(ascending=False)


def rank_features(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    top_k: int = config.CLASSICAL_TOP_K,
) -> dict:
    """
    Run all four methods and return an ensemble ranking.

    Returns
    -------
    dict with keys:
      rankings   – dict[method_name → pd.Series of importance scores]
      top_features – list of *top_k* feature names by ensemble vote
      votes      – pd.Series of vote counts per feature
    """
    methods = {
        "xgboost": _xgb_importance,
        "random_forest": _rf_importance,
        "mutual_info": _mutual_info,
        "chi_squared": _chi_squared,
    }

    rankings: dict[str, pd.Series] = {}
    vote_pool: list[str] = []

    for name, fn in methods.items():
        print(f"[classical-fs] Running {name} …")
        ranking = fn(X, y, feature_names)
        rankings[name] = ranking
        vote_pool.extend(ranking.head(top_k).index.tolist())

    votes = pd.Series(vote_pool).value_counts()
    top_features = votes.head(top_k).index.tolist()

    print(f"[classical-fs] Ensemble top-{top_k} features: {top_features}")

    return dict(rankings=rankings, top_features=top_features, votes=votes)


def select_features(
    X: np.ndarray,
    feature_names: list[str],
    selected: list[str],
) -> tuple[np.ndarray, list[int]]:
    """Return X filtered to only *selected* columns."""
    indices = [feature_names.index(f) for f in selected]
    return X[:, indices], indices
