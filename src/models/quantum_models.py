"""
Quantum SVM (QSVM) model using Qiskit's FidelityQuantumKernel.

The model:
  1. Builds a ZZFeatureMap quantum circuit for the given feature dimension.
  2. Computes a quantum kernel matrix via FidelityQuantumKernel.
  3. Trains a classical SVC with the precomputed quantum kernel.
"""
from __future__ import annotations

import time
import warnings
import numpy as np
from sklearn.svm import SVC

from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.kernels import FidelityQuantumKernel

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import config


def _sanitize_kernel(K: np.ndarray) -> np.ndarray:
    """Replace NaN/Inf in kernel matrix and ensure diagonal = 1."""
    K = np.nan_to_num(K, nan=0.0, posinf=1.0, neginf=0.0)
    np.fill_diagonal(K, 1.0)
    return K


class QSVMModel:
    """Quantum Support Vector Machine backed by a ZZFeatureMap kernel."""

    def __init__(self, n_features: int, reps: int = config.QSVM_REPS):
        self.n_features = n_features
        if n_features < 2:
            from qiskit.circuit.library import ZFeatureMap
            self.feature_map = ZFeatureMap(feature_dimension=n_features, reps=reps)
        else:
            self.feature_map = ZZFeatureMap(
                feature_dimension=n_features,
                reps=reps,
                entanglement="linear",
            )
        self.kernel = FidelityQuantumKernel(feature_map=self.feature_map)
        self.svc = SVC(kernel="precomputed", probability=True)
        self.X_train: np.ndarray | None = None
        self.train_time: float = 0.0
        self.predict_time: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "QSVMModel":
        t0 = time.time()
        self.X_train = X
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            kernel_matrix = _sanitize_kernel(self.kernel.evaluate(X))
        self.svc.fit(kernel_matrix, y)
        self.train_time = time.time() - t0
        print(f"[QSVM] Trained on {X.shape[0]} samples, "
              f"{self.n_features} features in {self.train_time:.2f}s")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        t0 = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            kernel_matrix = _sanitize_kernel(self.kernel.evaluate(X, self.X_train))
        preds = self.svc.predict(kernel_matrix)
        self.predict_time = time.time() - t0
        return preds

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        t0 = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            kernel_matrix = _sanitize_kernel(self.kernel.evaluate(X, self.X_train))
        proba = self.svc.predict_proba(kernel_matrix)[:, 1]
        self.predict_time = time.time() - t0
        return proba
