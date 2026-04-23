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
from pathlib import Path
import numpy as np
import joblib
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


def _build_feature_map(n_features: int, reps: int):
    if n_features < 2:
        from qiskit.circuit.library import ZFeatureMap
        return ZFeatureMap(feature_dimension=n_features, reps=reps)
    return ZZFeatureMap(
        feature_dimension=n_features,
        reps=reps,
        entanglement="linear",
    )


class QSVMModel:
    """Quantum Support Vector Machine backed by a ZZFeatureMap kernel."""

    def __init__(self, n_features: int, reps: int = config.QSVM_REPS):
        self.n_features = n_features
        self.reps = reps
        self.feature_map = _build_feature_map(n_features, reps)
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

    def _test_kernel(self, X: np.ndarray) -> np.ndarray:
        """Compute kernel matrix between X and the training set (expensive)."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return _sanitize_kernel(self.kernel.evaluate(X, self.X_train))

    def predict(self, X: np.ndarray) -> np.ndarray:
        t0 = time.time()
        preds = self.svc.predict(self._test_kernel(X))
        self.predict_time = time.time() - t0
        return preds

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        t0 = time.time()
        proba = self.svc.predict_proba(self._test_kernel(X))[:, 1]
        self.predict_time = time.time() - t0
        return proba

    def evaluate(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return (predictions, probabilities) computing the kernel only once."""
        t0 = time.time()
        K = self._test_kernel(X)
        preds = self.svc.predict(K)
        proba = self.svc.predict_proba(K)[:, 1]
        self.predict_time = time.time() - t0
        return preds, proba

    def save(self, directory: Path) -> None:
        """Persist QSVM to *directory* (SVC, training data, and config)."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.svc, directory / "qsvm_svc.pkl")
        np.save(directory / "qsvm_X_train.npy", self.X_train)
        joblib.dump(
            {"n_features": self.n_features, "reps": self.reps},
            directory / "qsvm_meta.pkl",
        )
        print(f"[QSVM] Saved to {directory}")

    @classmethod
    def load(cls, directory: Path) -> "QSVMModel":
        """Reconstruct a trained QSVM from saved artefacts."""
        directory = Path(directory)
        meta = joblib.load(directory / "qsvm_meta.pkl")
        model = cls(n_features=meta["n_features"], reps=meta["reps"])
        model.svc = joblib.load(directory / "qsvm_svc.pkl")
        model.X_train = np.load(directory / "qsvm_X_train.npy")
        print(f"[QSVM] Loaded from {directory}  "
              f"({model.X_train.shape[0]} support vectors, "
              f"{model.n_features} features)")
        return model
