# Improving Quantum-Classical Methods for Credit Card Fraud Detection

> **BE Project** — Based on *"Mixed Quantum-Classical Method for Fraud Detection With Quantum Feature Selection"*, with a novel two-step feature selection pipeline.

---

## Project Overview

This project compares three approaches to credit-card fraud detection:

| Scenario | Feature Selection | Models | Ensemble |
|----------|-------------------|--------|----------|
| **1 — Classical Only** | XGBoost / RF / MI / Chi² | XGBoost, Random Forest | — |
| **2 — Base Paper** | Quantum (QSVM) | XGBoost, RF, QSVM | — |
| **3 — Improved (Ours)** | Classical → Quantum (two-step) | XGBoost, RF, QSVM | Weighted avg + Meta-clf |

**Key improvement**: Instead of running quantum feature selection on all 69 features (expensive), we first use classical methods to reduce to ~15 features, then apply QSVM-based quantum selection to pick the final 5–7. This cuts quantum computation cost while preserving (or improving) accuracy.

---

## Repository Structure

```
BE Project/
├── config.py                        # Central configuration
├── requirements.txt                 # Python dependencies
├── README.md
├── data/
│   └── creditcard.csv               # ← Place dataset here
├── src/
│   ├── __init__.py
│   ├── data_preparation.py          # Loading, cleaning, scaling, balancing
│   ├── classical_feature_selection.py  # XGBoost/RF/MI/Chi² feature ranking
│   ├── quantum_feature_selection.py    # QSVM greedy forward selection
│   ├── evaluation.py                # Metrics computation
│   ├── visualization.py             # Plotting utilities
│   ├── utils.py                     # Helpers (seeding, saving, timing)
│   └── models/
│       ├── __init__.py
│       ├── classical_models.py      # XGBoost & Random Forest wrappers
│       ├── quantum_models.py        # QSVM (Qiskit)
│       └── ensemble.py             # Weighted averaging & meta-classifier
├── scripts/
│   ├── run_scenario1_classical.py   # Scenario 1 runner
│   ├── run_scenario2_base_paper.py  # Scenario 2 runner
│   ├── run_scenario3_improved.py    # Scenario 3 runner
│   └── run_all_scenarios.py         # Master runner with plots
├── notebooks/
│   └── exploration.ipynb            # Interactive exploration notebook
└── results/
    ├── plots/                       # Generated plots (PNG)
    └── tables/                      # Metric CSVs and JSONs
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place the dataset

Download the credit card fraud dataset (with ~69 features) and place it at:
```
data/creditcard.csv
```

The target column should be named `Class` (1 = fraud, 0 = legitimate). If your dataset uses a different name, update `TARGET_COLUMN` in `config.py`.

### 3. (Optional) IBM Quantum access

To run on real quantum hardware, set your API token:
```bash
export IBM_QUANTUM_TOKEN="your_token_here"
```
and set `USE_SIMULATOR = False` in `config.py`.

---

## Running Experiments

### Run all three scenarios with comparison plots

```bash
python scripts/run_all_scenarios.py --dataset data/creditcard.csv
```

### Run individual scenarios

```bash
python scripts/run_scenario1_classical.py
python scripts/run_scenario2_base_paper.py
python scripts/run_scenario3_improved.py
```

### Multi-seed reliability test

```bash
python scripts/run_all_scenarios.py --reliability --n-seeds 5
```

### Interactive exploration

```bash
jupyter notebook notebooks/exploration.ipynb
```

---

## Methodology

### Two-Step Feature Selection (Our Contribution)

```
69 features ──► Classical Filtering ──► ~15 features ──► Quantum Selection ──► 5-7 features
                (XGBoost, RF, MI, χ²)                    (QSVM kernel accuracy)
```

**Step 1 — Classical Filtering**: Four methods (XGBoost importance, Random Forest importance, Mutual Information, Chi-squared) each rank all features. An ensemble vote selects the top 15.

**Step 2 — Quantum Selection**: Greedy forward selection using QSVM cross-validation accuracy as the scoring criterion narrows down to 5–7 features.

### Ensemble Methods

1. **Weighted Combination**: `score = w × quantum_score + (1-w) × classical_score`. Grid search over `w ∈ {0.0, 0.1, …, 1.0}`.
2. **Meta-Classifier**: A logistic regression trained on stacked quantum + classical predictions.

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Accuracy | Overall correctness |
| Precision | Of predicted frauds, how many are real |
| Recall / Hit Rate | Of real frauds, how many are detected |
| F1 Score | Harmonic mean of precision & recall |
| ROC-AUC | Area under ROC curve |
| PR-AUC | Area under precision-recall curve |
| False Alarm Rate | Legitimate transactions flagged as fraud |
| Training Time | Seconds to train the model |
| Prediction Time | Seconds to predict on test set |

---

## Generated Outputs

After running `run_all_scenarios.py`:

- **`results/tables/`** — CSV and JSON files with per-model metrics
- **`results/plots/roc_curves.png`** — ROC curves for all models
- **`results/plots/pr_curves.png`** — Precision-Recall curves
- **`results/plots/metric_comparison.png`** — Bar chart (F1, ROC-AUC, PR-AUC)
- **`results/plots/hit_vs_alarm.png`** — Hit Rate vs False Alarm scatter
- **`results/plots/feature_importance_heatmap.png`** — Feature ranking heatmap
- **`results/plots/weight_sweep.png`** — Ensemble weight tuning curve
- **`results/plots/timing_comparison.png`** — Training/prediction time bars

---

## Tools & Technologies

| Category | Tools |
|----------|-------|
| Classical ML | Python, scikit-learn, XGBoost |
| Quantum ML | Qiskit, Qiskit Machine Learning |
| Data Handling | Pandas, NumPy, imbalanced-learn |
| Visualization | Matplotlib, Seaborn |
| Notebooks | Jupyter |

---

## Configuration

All tuneable parameters are centralised in `config.py`:

- Dataset path, target column
- Number of features for classical/quantum selection
- Train/test split ratios, undersampling settings
- Quantum circuit parameters (reps, shots, backend)
- XGBoost and Random Forest hyperparameters
- Ensemble weight search range

---

## Expected Outcomes

1. The two-step approach should **improve accuracy and reliability** over pure quantum feature selection.
2. **Reduced quantum computation cost** by filtering irrelevant features classically first.
3. **Better balance** between hit rate and false alarm rate.
4. The quantum-classical ensemble should provide the **most robust fraud detection**.
