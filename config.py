"""
Central configuration for the Quantum-Classical Fraud Detection project.
"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
TABLES_DIR = RESULTS_DIR / "tables"

for d in (DATA_DIR, RESULTS_DIR, PLOTS_DIR, TABLES_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Dataset ────────────────────────────────────────────────────────────────────
TRAIN_PATH = DATA_DIR / "fraudTrain.csv"
TEST_PATH = DATA_DIR / "fraudTest.csv"
TARGET_COLUMN = "is_fraud"
RANDOM_STATE = 42
N_RANDOM_SEEDS = 5  # for reliability tests

# Columns to drop (identifiers, free-text, not useful for ML)
DROP_COLUMNS = [
    "Unnamed: 0", "trans_num", "cc_num",
    "first", "last", "street", "dob",
    "trans_date_trans_time",
]

# ── Feature selection ──────────────────────────────────────────────────────────
CLASSICAL_TOP_K = 15          # features kept after classical filtering
QUANTUM_TOP_K = 6             # features kept after quantum selection
MIN_QUANTUM_FEATURES = 5
MAX_QUANTUM_FEATURES = 7

# ── Data splits & balancing ────────────────────────────────────────────────────
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.15
UNDERSAMPLE_RATIO = 1.0       # 1:1 fraud-to-legitimate for classical
QUANTUM_SUBSET_SIZE = 200     # balanced subset size for quantum training (kept small for speed)

# ── Quantum settings ──────────────────────────────────────────────────────────
QSVM_REPS = 2                # ZZFeatureMap repetitions
QSVM_SHOTS = 1024
USE_SIMULATOR = True          # False → real IBM Quantum hardware
IBM_QUANTUM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN", "")
QUANTUM_BACKEND_NAME = "aer_simulator"

# ── Classical model hyper-parameters ───────────────────────────────────────────
XGBOOST_PARAMS = dict(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=1,
    eval_metric="logloss",
    use_label_encoder=False,
    random_state=RANDOM_STATE,
)

RF_PARAMS = dict(
    n_estimators=300,
    max_depth=10,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

# ── Ensemble ───────────────────────────────────────────────────────────────────
WEIGHT_SEARCH_RANGE = [round(w * 0.1, 1) for w in range(11)]  # 0.0 … 1.0

# ── Evaluation ─────────────────────────────────────────────────────────────────
METRIC_NAMES = [
    "accuracy", "precision", "recall", "f1",
    "roc_auc", "pr_auc", "hit_rate", "false_alarm_rate",
]
