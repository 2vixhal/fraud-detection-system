"""
Ensemble methods combining quantum and classical model predictions.

Two strategies:
  1. Weighted averaging:  score = w * quantum_score + (1-w) * classical_score
  2. Meta-classifier:     logistic regression over stacked predictions
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import config


class WeightedEnsemble:
    """Combine two probability vectors with a tunable weight."""

    def __init__(self, weight_quantum: float = 0.5):
        self.w = weight_quantum

    def combine(
        self, proba_quantum: np.ndarray, proba_classical: np.ndarray
    ) -> np.ndarray:
        return self.w * proba_quantum + (1 - self.w) * proba_classical

    @staticmethod
    def search_best_weight(
        proba_quantum: np.ndarray,
        proba_classical: np.ndarray,
        y_true: np.ndarray,
        metric_fn,
        weights: list[float] | None = None,
    ) -> tuple[float, float]:
        """
        Grid-search over weights and return (best_weight, best_score).

        Parameters
        ----------
        metric_fn : callable(y_true, y_score) → float
        """
        weights = weights or config.WEIGHT_SEARCH_RANGE
        best_w, best_s = 0.0, -1.0
        for w in weights:
            combined = w * proba_quantum + (1 - w) * proba_classical
            score = metric_fn(y_true, combined)
            if score > best_s:
                best_w, best_s = w, score
        print(f"[ensemble] Best weight w={best_w:.1f}  score={best_s:.4f}")
        return best_w, best_s


class MetaClassifier:
    """
    Stack quantum and classical predictions and learn a logistic
    regression meta-classifier on top.
    """

    def __init__(self):
        self.meta = LogisticRegression(max_iter=1000, random_state=config.RANDOM_STATE)

    def fit(
        self,
        proba_quantum: np.ndarray,
        proba_classical: np.ndarray,
        y: np.ndarray,
    ) -> "MetaClassifier":
        X_meta = np.column_stack([proba_quantum, proba_classical])
        self.meta.fit(X_meta, y)
        return self

    def predict_proba(
        self, proba_quantum: np.ndarray, proba_classical: np.ndarray
    ) -> np.ndarray:
        X_meta = np.column_stack([proba_quantum, proba_classical])
        return self.meta.predict_proba(X_meta)[:, 1]

    def predict(
        self, proba_quantum: np.ndarray, proba_classical: np.ndarray
    ) -> np.ndarray:
        X_meta = np.column_stack([proba_quantum, proba_classical])
        return self.meta.predict(X_meta)

    def cv_score(
        self,
        proba_quantum: np.ndarray,
        proba_classical: np.ndarray,
        y: np.ndarray,
        cv: int = 5,
    ) -> float:
        X_meta = np.column_stack([proba_quantum, proba_classical])
        scores = cross_val_score(self.meta, X_meta, y, cv=cv, scoring="roc_auc")
        mean_score = float(np.mean(scores))
        print(f"[meta-clf] CV ROC-AUC = {mean_score:.4f}")
        return mean_score
