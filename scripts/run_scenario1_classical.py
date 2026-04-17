#!/usr/bin/env python3
"""
Scenario 1 — Classical Only
  Feature selection : classical methods only
  Models            : XGBoost, Random Forest
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_preparation import prepare_data
from src.classical_feature_selection import rank_features, select_features
from src.models.classical_models import ClassicalModel
from src.evaluation import compute_metrics, compute_curves
from src.utils import set_seed, save_results
import config


def run(seed: int = config.RANDOM_STATE) -> dict:
    """Execute Scenario 1 and return metrics dict keyed by model name."""
    set_seed(seed)
    print("\n" + "=" * 60)
    print(f"  SCENARIO 1 — Classical Only  (seed={seed})")
    print("=" * 60)

    # ── Data ──────────────────────────────────────────────────────
    data = prepare_data(random_state=seed)

    # ── Feature selection (classical) ─────────────────────────────
    fs = rank_features(
        data["X_train_bal"], data["y_train_bal"], data["feature_names"],
        top_k=config.CLASSICAL_TOP_K,
    )
    selected = fs["top_features"]

    X_train, idx = select_features(data["X_train_bal"], data["feature_names"], selected)
    X_test = data["X_test"][:, idx]
    y_train = data["y_train_bal"]
    y_test = data["y_test"]

    # ── Train & evaluate ──────────────────────────────────────────
    results: dict[str, dict] = {}
    curves: dict[str, tuple] = {}

    for model_type in ("xgboost", "random_forest"):
        model = ClassicalModel(model_type)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)

        key = f"S1_{model_type}"
        results[key] = compute_metrics(
            y_test, y_pred, y_proba,
            train_time=model.train_time,
            predict_time=model.predict_time,
        )
        curves[key] = compute_curves(y_test, y_proba)

        print(f"\n[{key}]  F1={results[key]['f1']:.4f}  "
              f"ROC-AUC={results[key]['roc_auc']:.4f}  "
              f"PR-AUC={results[key]['pr_auc']:.4f}")

    return {"metrics": results, "curves": curves, "feature_selection": fs}


if __name__ == "__main__":
    out = run()
    save_results(out["metrics"], "scenario1_metrics")
