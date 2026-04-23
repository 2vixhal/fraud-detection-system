#!/usr/bin/env python3
"""
Train all models using the two-step feature selection pipeline and persist
every artefact needed by the backend API for real-time inference:

  results/models/
    xgboost.pkl          – fitted XGBClassifier
    qsvm_svc.pkl         – fitted SVC (precomputed kernel)
    qsvm_X_train.npy     – QSVM training data (needed for kernel at predict time)
    qsvm_meta.pkl        – {n_features, reps}
    scaler.pkl           – MinMaxScaler fitted on training data
    feature_meta.pkl     – {all_feature_names, selected_features, selected_indices,
                            ensemble_weight}
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import joblib
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import MinMaxScaler

from src.data_preparation import prepare_data
from src.classical_feature_selection import rank_features, select_features
from src.quantum_feature_selection import greedy_forward_selection
from src.models.classical_models import ClassicalModel
from src.models.quantum_models import QSVMModel
from src.models.ensemble import WeightedEnsemble
from src.evaluation import compute_metrics
from src.utils import set_seed
import config


PROCESSOR_FEATURES = {
    "amt", "merchant", "category", "hour", "day_of_week", "month",
    "age", "gender", "job", "lat", "long", "merch_lat", "merch_long",
    "distance", "lat_diff", "long_diff", "city_pop",
}


def main(seed: int = config.RANDOM_STATE) -> None:
    set_seed(seed)
    models_dir = config.MODELS_DIR

    print("=" * 60)
    print("  TRAINING PIPELINE — Two-Step Feature Selection")
    print("=" * 60)

    # ── 1. Data preparation ───────────────────────────────────────
    data = prepare_data(random_state=seed)

    # ── 2. Step 1: Classical feature selection (all → 15) ─────────
    classical_fs = rank_features(
        data["X_train_bal"], data["y_train_bal"], data["feature_names"],
        top_k=config.CLASSICAL_TOP_K,
    )
    classical_selected = classical_fs["top_features"]
    # Only keep features the TransactionProcessor can produce at
    # inference time, so the backend can actually use the trained model.
    classical_selected = [
        f for f in classical_selected if f in PROCESSOR_FEATURES
    ]
    if not classical_selected:
        raise RuntimeError("No processor-compatible features survived "
                           "classical selection")
    _, classical_idx = select_features(
        data["X_train_bal"], data["feature_names"], classical_selected,
    )
    print(f"[train] Classical step kept {len(classical_idx)} features: "
          f"{classical_selected}")

    # ── 3. Step 2: Quantum feature selection (15 → 5-7) ──────────
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
    print(f"[train] Final features after two-step selection: {final_features}")

    # ── 4. Prepare final matrices ─────────────────────────────────
    X_train = data["X_train_bal"][:, final_idx]
    X_test_full = data["X_test"][:, final_idx]
    y_train = data["y_train_bal"]
    y_test_full = data["y_test"]

    X_quantum = data["X_quantum"][:, final_idx]
    y_quantum = data["y_quantum"]

    # QSVM kernel evaluation is O(N_test × N_train) quantum circuits.
    # 200 eval samples × 200 train samples = 40K circuits ≈ 40 seconds.
    QSVM_EVAL_SIZE = 200
    rng = np.random.RandomState(seed)
    fraud_idx = np.where(y_test_full == 1)[0]
    legit_idx = np.where(y_test_full == 0)[0]
    half = QSVM_EVAL_SIZE // 2
    eval_idx = np.concatenate([
        rng.choice(fraud_idx, min(half, len(fraud_idx)), replace=False),
        rng.choice(legit_idx, min(half, len(legit_idx)), replace=False),
    ])
    rng.shuffle(eval_idx)
    X_test_small = X_test_full[eval_idx]
    y_test_small = y_test_full[eval_idx]
    print(f"[train] QSVM eval subset: {len(eval_idx)} samples "
          f"(fraud={int(y_test_small.sum())}, "
          f"legit={len(y_test_small)-int(y_test_small.sum())})")

    # ── 5. Train XGBoost ──────────────────────────────────────────
    xgb = ClassicalModel("xgboost")
    xgb.fit(X_train, y_train)
    xgb_proba_full = xgb.predict_proba(X_test_full)
    xgb_pred_full = xgb.predict(X_test_full)
    xgb_metrics = compute_metrics(y_test_full, xgb_pred_full, xgb_proba_full)
    print(f"[train] XGBoost  →  ROC-AUC={xgb_metrics['roc_auc']:.4f}  "
          f"F1={xgb_metrics['f1']:.4f}")

    # ── 6. Train QSVM ────────────────────────────────────────────
    qsvm = QSVMModel(n_features=len(final_idx))
    qsvm.fit(X_quantum, y_quantum)
    print("[train] Evaluating QSVM (kernel once for predict + proba) …")
    qsvm_pred, qsvm_proba = qsvm.evaluate(X_test_small)
    qsvm_metrics = compute_metrics(y_test_small, qsvm_pred, qsvm_proba)
    print(f"[train] QSVM     →  ROC-AUC={qsvm_metrics['roc_auc']:.4f}  "
          f"F1={qsvm_metrics['f1']:.4f}")

    # ── 7. Find best ensemble weight ──────────────────────────────
    xgb_proba_small = xgb.predict_proba(X_test_small)
    best_w, best_score = WeightedEnsemble.search_best_weight(
        qsvm_proba, xgb_proba_small, y_test_small,
        metric_fn=roc_auc_score,
    )
    print(f"[train] Best ensemble weight  →  w_quantum={best_w:.1f}  "
          f"ROC-AUC={best_score:.4f}")

    # ── 8. Save everything ────────────────────────────────────────
    xgb.save(models_dir / "xgboost.pkl")
    qsvm.save(models_dir)

    # Build a scaler that operates on the selected features only.
    # The training scaler covers all ~69 features; extract the sub-scaler
    # so the backend can scale just the 5-7 features it receives.
    full_scaler = data["scaler"]
    sel_scaler = MinMaxScaler(feature_range=full_scaler.feature_range)
    sel_scaler.n_features_in_ = len(final_idx)
    sel_scaler.data_min_ = full_scaler.data_min_[final_idx]
    sel_scaler.data_max_ = full_scaler.data_max_[final_idx]
    sel_scaler.data_range_ = full_scaler.data_range_[final_idx]
    sel_scaler.scale_ = full_scaler.scale_[final_idx]
    sel_scaler.min_ = full_scaler.min_[final_idx]

    joblib.dump(sel_scaler, models_dir / "scaler.pkl")
    print(f"[train] Selected-feature scaler saved to {models_dir / 'scaler.pkl'}")

    feature_meta = {
        "all_feature_names": sorted(PROCESSOR_FEATURES),
        "selected_features": final_features,
        "selected_indices": final_idx,
        "ensemble_weight": best_w,
    }
    joblib.dump(feature_meta, models_dir / "feature_meta.pkl")
    print(f"[train] Feature metadata saved to {models_dir / 'feature_meta.pkl'}")

    # ── 9. Summary ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE — Saved artefacts")
    print("=" * 60)
    print(f"  Models dir         : {models_dir}")
    print(f"  Selected features  : {final_features}")
    print(f"  Ensemble weight    : {best_w}")
    print(f"  XGBoost ROC-AUC    : {xgb_metrics['roc_auc']:.4f}")
    print(f"  QSVM ROC-AUC      : {qsvm_metrics['roc_auc']:.4f}")
    print(f"  Ensemble ROC-AUC   : {best_score:.4f}")
    print("=" * 60)
    print("\nYou can now start the backend with real model inference.")


if __name__ == "__main__":
    main()
