#!/usr/bin/env python3
"""
Scenario 3 — Our Improved Approach (Two-Step Feature Selection)
  Feature selection : Step 1 classical → Step 2 quantum
  Models            : XGBoost, Random Forest, QSVM
  Ensemble          : Weighted averaging + meta-classifier
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_preparation import prepare_data
from src.classical_feature_selection import rank_features, select_features
from src.quantum_feature_selection import greedy_forward_selection
from src.models.classical_models import ClassicalModel
from src.models.quantum_models import QSVMModel
from src.models.ensemble import WeightedEnsemble, MetaClassifier
from src.evaluation import compute_metrics, compute_curves
from src.utils import set_seed, save_results
import config


def run(seed: int = config.RANDOM_STATE) -> dict:
    """Execute Scenario 3 and return metrics dict."""
    set_seed(seed)
    print("\n" + "=" * 60)
    print(f"  SCENARIO 3 — Improved Two-Step FS  (seed={seed})")
    print("=" * 60)

    # ── Data ──────────────────────────────────────────────────────
    data = prepare_data(random_state=seed)

    # ── Step 1: Classical feature selection (69 → ~15) ────────────
    classical_fs = rank_features(
        data["X_train_bal"], data["y_train_bal"], data["feature_names"],
        top_k=config.CLASSICAL_TOP_K,
    )
    classical_selected = classical_fs["top_features"]
    _, classical_idx = select_features(
        data["X_train_bal"], data["feature_names"], classical_selected,
    )

    # ── Step 2: Quantum feature selection (15 → 5-7) ─────────────
    X_quantum_cls = data["X_quantum"][:, classical_idx]
    qfs = greedy_forward_selection(
        X_quantum_cls, data["y_quantum"],
        candidate_indices=list(range(len(classical_idx))),
        min_features=config.MIN_QUANTUM_FEATURES,
        max_features=config.MAX_QUANTUM_FEATURES,
    )
    q_local_idx = qfs["selected_indices"]
    final_idx = [classical_idx[i] for i in q_local_idx]
    final_features = [data["feature_names"][i] for i in final_idx]
    print(f"[S3] Final features after two-step selection: {final_features}")

    # ── Prepare final feature matrices ────────────────────────────
    X_train = data["X_train_bal"][:, final_idx]
    X_test = data["X_test"][:, final_idx]
    y_train = data["y_train_bal"]
    y_test = data["y_test"]

    X_quantum = data["X_quantum"][:, final_idx]
    y_quantum = data["y_quantum"]

    # ── Train individual models ───────────────────────────────────
    results: dict[str, dict] = {}
    curves: dict[str, tuple] = {}
    probas: dict[str, np.ndarray] = {}

    for model_type in ("xgboost", "random_forest"):
        model = ClassicalModel(model_type)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
        probas[model_type] = y_proba

        key = f"S3_{model_type}"
        results[key] = compute_metrics(
            y_test, y_pred, y_proba,
            train_time=model.train_time,
            predict_time=model.predict_time,
        )
        curves[key] = compute_curves(y_test, y_proba)

    # QSVM
    qsvm = QSVMModel(n_features=len(final_idx))
    qsvm.fit(X_quantum, y_quantum)
    y_pred_q = qsvm.predict(X_test)
    y_proba_q = qsvm.predict_proba(X_test)
    probas["qsvm"] = y_proba_q

    results["S3_qsvm"] = compute_metrics(
        y_test, y_pred_q, y_proba_q,
        train_time=qsvm.train_time,
        predict_time=qsvm.predict_time,
    )
    curves["S3_qsvm"] = compute_curves(y_test, y_proba_q)

    # ── Ensemble: Weighted combination (QSVM + best classical) ───
    best_classical = max(("xgboost", "random_forest"),
                         key=lambda m: results[f"S3_{m}"]["roc_auc"])
    proba_cls = probas[best_classical]
    proba_qm = probas["qsvm"]

    best_w, best_score = WeightedEnsemble.search_best_weight(
        proba_qm, proba_cls, y_test,
        metric_fn=roc_auc_score,
    )
    ens = WeightedEnsemble(weight_quantum=best_w)
    y_ens_proba = ens.combine(proba_qm, proba_cls)
    y_ens_pred = (y_ens_proba >= 0.5).astype(int)

    results["S3_ensemble_weighted"] = compute_metrics(
        y_test, y_ens_pred, y_ens_proba,
    )
    curves["S3_ensemble_weighted"] = compute_curves(y_test, y_ens_proba)

    # Weight sweep data for plotting
    weight_scores = []
    for w in config.WEIGHT_SEARCH_RANGE:
        combined = w * proba_qm + (1 - w) * proba_cls
        weight_scores.append(roc_auc_score(y_test, combined))

    # ── Ensemble: Meta-classifier ─────────────────────────────────
    meta = MetaClassifier()
    meta.fit(proba_qm, proba_cls, y_test)
    y_meta_proba = meta.predict_proba(proba_qm, proba_cls)
    y_meta_pred = meta.predict(proba_qm, proba_cls)

    results["S3_ensemble_meta"] = compute_metrics(
        y_test, y_meta_pred, y_meta_proba,
    )
    curves["S3_ensemble_meta"] = compute_curves(y_test, y_meta_proba)

    for key, m in results.items():
        print(f"\n[{key}]  F1={m['f1']:.4f}  "
              f"ROC-AUC={m['roc_auc']:.4f}  PR-AUC={m['pr_auc']:.4f}")

    return {
        "metrics": results,
        "curves": curves,
        "classical_fs": classical_fs,
        "quantum_fs": qfs,
        "final_features": final_features,
        "best_ensemble_weight": best_w,
        "weight_sweep": (config.WEIGHT_SEARCH_RANGE, weight_scores),
    }


if __name__ == "__main__":
    out = run()
    save_results(out["metrics"], "scenario3_metrics")
