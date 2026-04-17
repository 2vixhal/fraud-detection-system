#!/usr/bin/env python3
"""
Scenario 2 — Base Paper Approach
  Feature selection : quantum only (QSVM-based)
  Models            : XGBoost, Random Forest, QSVM
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_preparation import prepare_data
from src.quantum_feature_selection import greedy_forward_selection
from src.models.classical_models import ClassicalModel
from src.models.quantum_models import QSVMModel
from src.evaluation import compute_metrics, compute_curves
from src.utils import set_seed, save_results
import config


def run(seed: int = config.RANDOM_STATE) -> dict:
    """Execute Scenario 2 and return metrics dict."""
    set_seed(seed)
    print("\n" + "=" * 60)
    print(f"  SCENARIO 2 — Base Paper (Quantum FS)  (seed={seed})")
    print("=" * 60)

    # ── Data ──────────────────────────────────────────────────────
    data = prepare_data(random_state=seed)
    n_features = len(data["feature_names"])

    # ── Feature selection (quantum only — on small subset) ────────
    candidate_indices = list(range(n_features))
    qfs = greedy_forward_selection(
        data["X_quantum"], data["y_quantum"],
        candidate_indices=candidate_indices,
        min_features=config.MIN_QUANTUM_FEATURES,
        max_features=config.MAX_QUANTUM_FEATURES,
    )
    sel_idx = qfs["selected_indices"]
    selected_names = [data["feature_names"][i] for i in sel_idx]
    print(f"[S2] Quantum-selected features: {selected_names}")

    X_train_bal = data["X_train_bal"][:, sel_idx]
    X_test = data["X_test"][:, sel_idx]
    y_train_bal = data["y_train_bal"]
    y_test = data["y_test"]

    X_quantum = data["X_quantum"][:, sel_idx]
    y_quantum = data["y_quantum"]

    # ── Train & evaluate ──────────────────────────────────────────
    results: dict[str, dict] = {}
    curves: dict[str, tuple] = {}

    # Classical models on quantum-selected features
    for model_type in ("xgboost", "random_forest"):
        model = ClassicalModel(model_type)
        model.fit(X_train_bal, y_train_bal)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)

        key = f"S2_{model_type}"
        results[key] = compute_metrics(
            y_test, y_pred, y_proba,
            train_time=model.train_time,
            predict_time=model.predict_time,
        )
        curves[key] = compute_curves(y_test, y_proba)

    # QSVM on quantum-selected features
    qsvm = QSVMModel(n_features=len(sel_idx))
    qsvm.fit(X_quantum, y_quantum)
    y_pred_q = qsvm.predict(X_test)
    y_proba_q = qsvm.predict_proba(X_test)

    results["S2_qsvm"] = compute_metrics(
        y_test, y_pred_q, y_proba_q,
        train_time=qsvm.train_time,
        predict_time=qsvm.predict_time,
    )
    curves["S2_qsvm"] = compute_curves(y_test, y_proba_q)

    for key, m in results.items():
        print(f"\n[{key}]  F1={m['f1']:.4f}  "
              f"ROC-AUC={m['roc_auc']:.4f}  PR-AUC={m['pr_auc']:.4f}")

    return {
        "metrics": results,
        "curves": curves,
        "quantum_fs": qfs,
        "selected_features": selected_names,
    }


if __name__ == "__main__":
    out = run()
    save_results(out["metrics"], "scenario2_metrics")
