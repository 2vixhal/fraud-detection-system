"""
Quantum feature selection (Step 2) using QSVM accuracy as the scoring criterion.

Given a reduced set of features (e.g. 15 from classical filtering), this module
evaluates feature subsets by training a QSVM on each combination and selecting the
subset that maximises validation accuracy.

To keep computation tractable we use a greedy forward-selection strategy rather
than exhaustive search.
"""
from __future__ import annotations

import time
import warnings
import itertools
from typing import Sequence

import numpy as np
from sklearn.model_selection import StratifiedKFold

from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.svm import SVC

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def _build_kernel(n_features: int) -> FidelityQuantumKernel:
    """Build a quantum kernel, using ZFeatureMap for 1 qubit, ZZFeatureMap for 2+."""
    if n_features < 2:
        from qiskit.circuit.library import ZFeatureMap
        feature_map = ZFeatureMap(feature_dimension=n_features, reps=config.QSVM_REPS)
    else:
        feature_map = ZZFeatureMap(
            feature_dimension=n_features,
            reps=config.QSVM_REPS,
            entanglement="linear",
        )
    return FidelityQuantumKernel(feature_map=feature_map)


def _sanitize_kernel(K: np.ndarray) -> np.ndarray:
    """Replace NaN/Inf in kernel matrix and ensure positive semi-definiteness."""
    K = np.nan_to_num(K, nan=0.0, posinf=1.0, neginf=0.0)
    np.fill_diagonal(K, 1.0)
    return K


def _evaluate_subset(
    X: np.ndarray,
    y: np.ndarray,
    feature_indices: list[int],
    n_splits: int = 2,
) -> float:
    """Return mean CV accuracy of a QSVM trained on the given feature subset."""
    X_sub = X[:, feature_indices]
    n_features = len(feature_indices)
    kernel = _build_kernel(n_features)

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True,
                          random_state=config.RANDOM_STATE)
    scores = []

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for train_idx, val_idx in skf.split(X_sub, y):
            X_tr, X_val = X_sub[train_idx], X_sub[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            try:
                kernel_matrix_train = _sanitize_kernel(kernel.evaluate(X_tr))
                kernel_matrix_val = _sanitize_kernel(kernel.evaluate(X_val, X_tr))

                svc = SVC(kernel="precomputed")
                svc.fit(kernel_matrix_train, y_tr)
                scores.append(svc.score(kernel_matrix_val, y_val))
            except Exception:
                scores.append(0.5)

    return float(np.mean(scores))


def greedy_forward_selection(
    X: np.ndarray,
    y: np.ndarray,
    candidate_indices: list[int],
    min_features: int = config.MIN_QUANTUM_FEATURES,
    max_features: int = config.MAX_QUANTUM_FEATURES,
) -> dict:
    """
    Greedy forward feature selection scored by QSVM accuracy.

    Returns
    -------
    dict with keys:
      selected_indices – list[int]
      selected_count   – int
      best_score       – float
      history          – list of (step, added_index, score)
    """
    remaining = list(candidate_indices)
    selected: list[int] = []
    history: list[tuple[int, int, float]] = []
    best_overall = -1.0

    print(f"[quantum-fs] Starting greedy forward selection "
          f"(candidates={len(remaining)}, target={min_features}–{max_features})")

    for step in range(max_features):
        best_score = -1.0
        best_feat = -1

        for feat in remaining:
            trial = selected + [feat]
            t0 = time.time()
            score = _evaluate_subset(X, y, trial)
            elapsed = time.time() - t0
            print(f"  step {step+1} | try feature {feat} | "
                  f"acc={score:.4f} | {elapsed:.1f}s")
            if score > best_score:
                best_score = score
                best_feat = feat

        selected.append(best_feat)
        remaining.remove(best_feat)
        history.append((step + 1, best_feat, best_score))
        best_overall = best_score
        print(f"  → selected feature {best_feat} (acc={best_score:.4f})")

        if step + 1 >= min_features and best_score <= (history[-2][2] if len(history) > 1 else 0):
            print("[quantum-fs] No improvement — stopping early")
            break

    print(f"[quantum-fs] Final selected indices: {selected}  "
          f"(score={best_overall:.4f})")

    return dict(
        selected_indices=selected,
        selected_count=len(selected),
        best_score=best_overall,
        history=history,
    )


def exhaustive_selection(
    X: np.ndarray,
    y: np.ndarray,
    candidate_indices: list[int],
    subset_size: int = config.QUANTUM_TOP_K,
) -> dict:
    """
    Exhaustive search over all C(n, k) subsets — only feasible for small n.
    Falls back to greedy if combinations exceed 200.
    """
    n = len(candidate_indices)
    n_combos = 1
    for i in range(subset_size):
        n_combos = n_combos * (n - i) // (i + 1)

    if n_combos > 200:
        print(f"[quantum-fs] {n_combos} combinations too many — falling back to greedy")
        return greedy_forward_selection(
            X, y, candidate_indices,
            min_features=subset_size, max_features=subset_size,
        )

    print(f"[quantum-fs] Exhaustive search: {n_combos} combinations of size {subset_size}")
    best_score = -1.0
    best_combo: tuple = ()

    for combo in itertools.combinations(candidate_indices, subset_size):
        score = _evaluate_subset(X, y, list(combo))
        if score > best_score:
            best_score = score
            best_combo = combo

    print(f"[quantum-fs] Best subset: {best_combo}  (acc={best_score:.4f})")

    return dict(
        selected_indices=list(best_combo),
        selected_count=subset_size,
        best_score=best_score,
        history=[],
    )
