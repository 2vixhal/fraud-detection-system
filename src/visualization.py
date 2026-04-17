"""
Plotting utilities for the Quantum-Classical Fraud Detection project.

Generates:
  - ROC curves (per scenario)
  - Precision-Recall curves
  - Bar charts comparing AUC and F1
  - Hit Rate vs False Alarm Rate comparison
  - Feature importance heatmap
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
SAVE_DIR = config.PLOTS_DIR


def _save(fig: plt.Figure, name: str) -> Path:
    path = SAVE_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] Saved {path}")
    return path


def plot_roc_curves(
    curves: dict[str, tuple[np.ndarray, np.ndarray]],
    aucs: dict[str, float] | None = None,
    title: str = "ROC Curve Comparison",
    filename: str = "roc_curves",
) -> Path:
    """Plot multiple ROC curves on one axis."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, (fpr, tpr) in curves.items():
        label = name
        if aucs and name in aucs:
            label += f" (AUC={aucs[name]:.3f})"
        ax.plot(fpr, tpr, linewidth=2, label=label)
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right")
    return _save(fig, filename)


def plot_pr_curves(
    curves: dict[str, tuple[np.ndarray, np.ndarray]],
    aucs: dict[str, float] | None = None,
    title: str = "Precision-Recall Curve Comparison",
    filename: str = "pr_curves",
) -> Path:
    """Plot multiple Precision-Recall curves."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, (recall, precision) in curves.items():
        label = name
        if aucs and name in aucs:
            label += f" (AP={aucs[name]:.3f})"
        ax.plot(recall, precision, linewidth=2, label=label)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(title)
    ax.legend(loc="upper right")
    return _save(fig, filename)


def plot_metric_bars(
    df: pd.DataFrame,
    metrics: list[str] | None = None,
    title: str = "Model Comparison",
    filename: str = "metric_comparison",
) -> Path:
    """Grouped bar chart for selected metrics across models."""
    metrics = metrics or ["f1", "roc_auc", "pr_auc"]
    plot_df = df[metrics].copy()

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_df.plot(kind="bar", ax=ax, edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Score")
    ax.set_title(title)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(title="Metric")
    ax.set_ylim(0, 1.05)

    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=7, padding=2)

    return _save(fig, filename)


def plot_hit_vs_alarm(
    df: pd.DataFrame,
    title: str = "Hit Rate vs False Alarm Rate",
    filename: str = "hit_vs_alarm",
) -> Path:
    """Scatter plot: hit rate (y) vs false alarm rate (x) per model."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for model in df.index:
        ax.scatter(
            df.loc[model, "false_alarm_rate"],
            df.loc[model, "hit_rate"],
            s=120, zorder=5, label=model,
        )
    ax.set_xlabel("False Alarm Rate")
    ax.set_ylabel("Hit Rate (Recall)")
    ax.set_title(title)
    ax.legend()
    ax.set_xlim(-0.02, max(0.15, df["false_alarm_rate"].max() * 1.2))
    ax.set_ylim(0, 1.05)
    return _save(fig, filename)


def plot_feature_importance_heatmap(
    rankings: dict[str, pd.Series],
    top_k: int = 15,
    title: str = "Feature Importance Heatmap",
    filename: str = "feature_importance_heatmap",
) -> Path:
    """Heatmap of normalised feature-importance scores across methods."""
    df = pd.DataFrame(rankings)
    all_features = set()
    for s in df.columns:
        all_features.update(df[s].head(top_k).index.tolist())

    df_top = df.loc[list(all_features)].fillna(0)
    df_norm = df_top.apply(lambda c: c / c.max() if c.max() > 0 else c)

    fig, ax = plt.subplots(figsize=(10, max(6, len(df_norm) * 0.35)))
    sns.heatmap(df_norm, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax,
                linewidths=0.5)
    ax.set_title(title)
    ax.set_ylabel("Feature")
    return _save(fig, filename)


def plot_timing_comparison(
    df: pd.DataFrame,
    title: str = "Training & Prediction Time",
    filename: str = "timing_comparison",
) -> Path:
    """Horizontal bar chart comparing train/predict times."""
    time_cols = [c for c in df.columns if c.endswith("_time_s")]
    if not time_cols:
        print("[plot] No timing columns found — skipping")
        return SAVE_DIR / f"{filename}.png"

    fig, ax = plt.subplots(figsize=(10, 5))
    df[time_cols].plot(kind="barh", ax=ax, edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Time (seconds)")
    ax.set_title(title)
    return _save(fig, filename)


def plot_weight_sweep(
    weights: list[float],
    scores: list[float],
    metric_name: str = "ROC-AUC",
    filename: str = "weight_sweep",
) -> Path:
    """Line plot showing ensemble score vs quantum weight."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(weights, scores, "o-", linewidth=2, markersize=6)
    best_idx = int(np.argmax(scores))
    ax.axvline(weights[best_idx], color="red", linestyle="--", alpha=0.6,
               label=f"best w={weights[best_idx]:.1f}")
    ax.set_xlabel("Quantum Weight (w)")
    ax.set_ylabel(metric_name)
    ax.set_title(f"Ensemble Weight Sweep — {metric_name}")
    ax.legend()
    return _save(fig, filename)
