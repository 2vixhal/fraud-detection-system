"""
Evaluation metrics for fraud detection.

Metrics: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC,
         Hit Rate (= Recall), False Alarm Rate (= FPR).
Also captures training/prediction times.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
    train_time: float = 0.0,
    predict_time: float = 0.0,
) -> dict[str, float]:
    """
    Return a flat dictionary of all evaluation metrics.

    Parameters
    ----------
    y_true   : ground-truth labels
    y_pred   : hard predictions
    y_proba  : predicted probabilities for the positive class (optional)
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "hit_rate": tp / (tp + fn) if (tp + fn) > 0 else 0.0,
        "false_alarm_rate": fp / (fp + tn) if (fp + tn) > 0 else 0.0,
        "train_time_s": train_time,
        "predict_time_s": predict_time,
    }

    if y_proba is not None:
        metrics["roc_auc"] = roc_auc_score(y_true, y_proba)
        metrics["pr_auc"] = average_precision_score(y_true, y_proba)
    else:
        metrics["roc_auc"] = np.nan
        metrics["pr_auc"] = np.nan

    return metrics


def compute_curves(
    y_true: np.ndarray, y_proba: np.ndarray
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Return ROC and PR curve arrays for plotting."""
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    prec, rec, _ = precision_recall_curve(y_true, y_proba)
    return {"roc": (fpr, tpr), "pr": (rec, prec)}


def metrics_to_dataframe(results: dict[str, dict]) -> pd.DataFrame:
    """
    Convert {scenario_model: metrics_dict, …} to a comparison DataFrame.
    """
    df = pd.DataFrame(results).T
    df.index.name = "model"
    return df.round(4)


def aggregate_multi_seed(
    all_results: list[dict[str, dict]],
) -> pd.DataFrame:
    """
    Given a list of per-seed result dicts, compute mean ± std for every metric.
    """
    frames = [metrics_to_dataframe(r) for r in all_results]
    combined = pd.concat(frames)
    grouped = combined.groupby(combined.index)

    mean = grouped.mean().round(4)
    std = grouped.std().round(4)

    summary = mean.astype(str) + " ± " + std.astype(str)
    summary.index.name = "model"
    return summary
