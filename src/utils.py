"""
Shared utility helpers.
"""
from __future__ import annotations

import json
import time
import random
from pathlib import Path

import numpy as np
import pandas as pd

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def set_seed(seed: int = config.RANDOM_STATE) -> None:
    """Set random seed for reproducibility across numpy and stdlib."""
    random.seed(seed)
    np.random.seed(seed)


def timer(label: str = ""):
    """Context manager that prints elapsed time."""
    class _Timer:
        def __init__(self):
            self.elapsed = 0.0
        def __enter__(self):
            self._t0 = time.time()
            return self
        def __exit__(self, *_):
            self.elapsed = time.time() - self._t0
            if label:
                print(f"[timer] {label}: {self.elapsed:.2f}s")
    return _Timer()


def save_results(results: dict, filename: str, directory: Path = config.TABLES_DIR) -> Path:
    """Save results dict as both CSV and JSON."""
    directory.mkdir(parents=True, exist_ok=True)

    if isinstance(results, dict) and all(isinstance(v, dict) for v in results.values()):
        df = pd.DataFrame(results).T
        csv_path = directory / f"{filename}.csv"
        df.to_csv(csv_path)
        print(f"[save] CSV → {csv_path}")
    else:
        csv_path = None

    json_path = directory / f"{filename}.json"
    serializable = _make_serializable(results)
    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"[save] JSON → {json_path}")

    return csv_path or json_path


def _make_serializable(obj):
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return round(float(obj), 6)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Series):
        return obj.to_dict()
    return obj
