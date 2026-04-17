#!/usr/bin/env python3
"""
Master runner — executes all three scenarios, generates comparison
tables and plots, and optionally runs multi-seed reliability tests.
"""
from __future__ import annotations

import argparse
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd

from scripts.run_scenario1_classical import run as run_s1
from scripts.run_scenario2_base_paper import run as run_s2
from scripts.run_scenario3_improved import run as run_s3
from src.evaluation import metrics_to_dataframe, aggregate_multi_seed
from src.visualization import (
    plot_roc_curves,
    plot_pr_curves,
    plot_metric_bars,
    plot_hit_vs_alarm,
    plot_feature_importance_heatmap,
    plot_timing_comparison,
    plot_weight_sweep,
)
from src.utils import save_results, set_seed
import config


def run_single(seed: int) -> dict:
    """Run all three scenarios with one seed and merge results."""
    out1 = run_s1(seed=seed)
    out2 = run_s2(seed=seed)
    out3 = run_s3(seed=seed)

    all_metrics = {}
    all_metrics.update(out1["metrics"])
    all_metrics.update(out2["metrics"])
    all_metrics.update(out3["metrics"])

    all_curves = {}
    all_curves.update(out1["curves"])
    all_curves.update(out2["curves"])
    all_curves.update(out3["curves"])

    return {
        "metrics": all_metrics,
        "curves": all_curves,
        "scenario1": out1,
        "scenario3": out3,
    }


def generate_plots(merged: dict) -> None:
    """Generate all comparison plots from merged results."""
    metrics = merged["metrics"]
    curves = merged["curves"]
    df = metrics_to_dataframe(metrics)

    roc_data = {k: v["roc"] for k, v in curves.items()}
    roc_aucs = {k: metrics[k]["roc_auc"] for k in curves}
    plot_roc_curves(roc_data, aucs=roc_aucs)

    pr_data = {k: v["pr"] for k, v in curves.items()}
    pr_aucs = {k: metrics[k]["pr_auc"] for k in curves}
    plot_pr_curves(pr_data, aucs=pr_aucs)

    plot_metric_bars(df, metrics=["f1", "roc_auc", "pr_auc"],
                     title="F1 / ROC-AUC / PR-AUC Comparison")

    plot_hit_vs_alarm(df)
    plot_timing_comparison(df)

    s1 = merged.get("scenario1", {})
    fs = s1.get("feature_selection", {})
    if "rankings" in fs:
        plot_feature_importance_heatmap(fs["rankings"])

    s3 = merged.get("scenario3", {})
    if "weight_sweep" in s3:
        weights, scores = s3["weight_sweep"]
        plot_weight_sweep(weights, scores)


def run_reliability(n_seeds: int = config.N_RANDOM_SEEDS) -> pd.DataFrame:
    """Run all scenarios across multiple seeds and aggregate."""
    all_results = []
    for i in range(n_seeds):
        seed = config.RANDOM_STATE + i * 7
        print(f"\n{'#' * 60}")
        print(f"  RELIABILITY RUN {i+1}/{n_seeds}  (seed={seed})")
        print(f"{'#' * 60}")
        merged = run_single(seed=seed)
        all_results.append(merged["metrics"])

    summary = aggregate_multi_seed(all_results)
    summary_path = config.TABLES_DIR / "reliability_summary.csv"
    summary.to_csv(summary_path)
    print(f"\n[reliability] Summary saved to {summary_path}")
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run Quantum-Classical Fraud Detection experiments"
    )
    parser.add_argument("--seed", type=int, default=config.RANDOM_STATE)
    parser.add_argument("--reliability", action="store_true",
                        help="Run multi-seed reliability tests")
    parser.add_argument("--n-seeds", type=int, default=config.N_RANDOM_SEEDS)
    args = parser.parse_args()

    if args.reliability:
        summary = run_reliability(n_seeds=args.n_seeds)
        print("\n=== Reliability Summary ===")
        print(summary)
    else:
        merged = run_single(seed=args.seed)

        df = metrics_to_dataframe(merged["metrics"])
        save_results(merged["metrics"], "all_scenarios_metrics")

        print("\n" + "=" * 60)
        print("  FINAL COMPARISON TABLE")
        print("=" * 60)
        print(df.to_string())

        generate_plots(merged)

        print(f"\n[done] Results in {config.TABLES_DIR}")
        print(f"[done] Plots   in {config.PLOTS_DIR}")


if __name__ == "__main__":
    main()
