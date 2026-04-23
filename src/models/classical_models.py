"""
Classical ML models: XGBoost and Random Forest classifiers.
"""
from __future__ import annotations

import time
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import config


class ClassicalModel:
    """Unified wrapper around XGBoost / Random Forest."""

    def __init__(self, model_type: str = "xgboost"):
        if model_type == "xgboost":
            self.model = XGBClassifier(**config.XGBOOST_PARAMS)
        elif model_type == "random_forest":
            self.model = RandomForestClassifier(**config.RF_PARAMS)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
        self.model_type = model_type
        self.train_time: float = 0.0
        self.predict_time: float = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ClassicalModel":
        t0 = time.time()
        self.model.fit(X, y)
        self.train_time = time.time() - t0
        print(f"[{self.model_type}] Trained in {self.train_time:.2f}s")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        t0 = time.time()
        preds = self.model.predict(X)
        self.predict_time = time.time() - t0
        return preds

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        t0 = time.time()
        proba = self.model.predict_proba(X)[:, 1]
        self.predict_time = time.time() - t0
        return proba

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        print(f"[{self.model_type}] Saved to {path}")

    @classmethod
    def load(cls, path: Path, model_type: str = "xgboost") -> "ClassicalModel":
        wrapper = cls.__new__(cls)
        wrapper.model = joblib.load(path)
        wrapper.model_type = model_type
        wrapper.train_time = 0.0
        wrapper.predict_time = 0.0
        print(f"[{model_type}] Loaded from {path}")
        return wrapper
