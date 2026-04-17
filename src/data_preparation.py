"""
Data loading, feature engineering, scaling, and class-balancing utilities.

Handles the simulated credit-card fraud dataset (fraudTrain.csv / fraudTest.csv)
with columns like merchant, category, amt, gender, city, state, lat/long, etc.

Pipeline:
  1. Load separate train/test CSVs
  2. Feature engineering (time features, age, distance, encoding)
  3. Drop identifier / free-text columns
  4. Scale numerics to [-1, 1] for quantum compatibility
  5. Create balanced subsets via undersampling
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from imblearn.under_sampling import RandomUnderSampler

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ── Loading ────────────────────────────────────────────────────────────────────

def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load train and test CSVs."""
    df_train = pd.read_csv(config.TRAIN_PATH)
    df_test = pd.read_csv(config.TEST_PATH)
    print(f"[data] Train: {df_train.shape[0]} rows, {df_train.shape[1]} cols")
    print(f"[data] Test : {df_test.shape[0]} rows, {df_test.shape[1]} cols")
    print(f"[data] Fraud rate — train: {df_train[config.TARGET_COLUMN].mean():.4f}, "
          f"test: {df_test[config.TARGET_COLUMN].mean():.4f}")
    return df_train, df_test


# ── Feature engineering ────────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features from raw transaction data."""
    df = df.copy()

    # Time-based features from trans_date_trans_time
    if "trans_date_trans_time" in df.columns:
        dt = pd.to_datetime(df["trans_date_trans_time"])
        df["hour"] = dt.dt.hour
        df["day_of_week"] = dt.dt.dayofweek
        df["month"] = dt.dt.month

    # Age from date of birth
    if "dob" in df.columns:
        dob = pd.to_datetime(df["dob"], errors="coerce")
        ref_date = pd.Timestamp("2019-06-01")
        df["age"] = ((ref_date - dob).dt.days / 365.25).round(1)

    # Distance between customer and merchant
    if all(c in df.columns for c in ["lat", "long", "merch_lat", "merch_long"]):
        df["lat_diff"] = abs(df["lat"] - df["merch_lat"])
        df["long_diff"] = abs(df["long"] - df["merch_long"])
        df["distance"] = np.sqrt(df["lat_diff"] ** 2 + df["long_diff"] ** 2)

    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode categorical columns."""
    df = df.copy()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    cat_cols = [c for c in cat_cols if c != config.TARGET_COLUMN]

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    if cat_cols:
        print(f"[data] Encoded {len(cat_cols)} categorical columns: {cat_cols}")
    return df


def clean_and_drop(df: pd.DataFrame) -> pd.DataFrame:
    """Remove identifier columns and handle missing values."""
    df = df.copy()
    to_drop = [c for c in config.DROP_COLUMNS if c in df.columns]
    df = df.drop(columns=to_drop, errors="ignore")
    before = len(df)
    df = df.drop_duplicates().dropna().reset_index(drop=True)
    if before != len(df):
        print(f"[data] Cleaned: {before} → {len(df)} rows")
    return df


# ── Scaling ────────────────────────────────────────────────────────────────────

def scale_features(
    X_train: np.ndarray,
    X_test: np.ndarray,
    feature_range: tuple[float, float] = (-1, 1),
) -> tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """Scale features to *feature_range* (default [-1, 1])."""
    scaler = MinMaxScaler(feature_range=feature_range)
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    return X_train_sc, X_test_sc, scaler


# ── Balancing ──────────────────────────────────────────────────────────────────

def undersample(
    X: np.ndarray,
    y: np.ndarray,
    ratio: float = config.UNDERSAMPLE_RATIO,
    random_state: int = config.RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray]:
    """Random undersampling of the majority class."""
    rus = RandomUnderSampler(sampling_strategy=ratio, random_state=random_state)
    X_res, y_res = rus.fit_resample(X, y)
    fraud_count = int(sum(y_res))
    print(f"[data] Undersampled: {len(y)} → {len(y_res)} "
          f"(fraud={fraud_count}, legit={len(y_res)-fraud_count})")
    return X_res, y_res


def create_quantum_subset(
    X: np.ndarray,
    y: np.ndarray,
    size: int = config.QUANTUM_SUBSET_SIZE,
    random_state: int = config.RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a small balanced subset suitable for quantum training."""
    rng = np.random.RandomState(random_state)
    fraud_idx = np.where(y == 1)[0]
    legit_idx = np.where(y == 0)[0]

    half = size // 2
    f_sample = rng.choice(fraud_idx, min(half, len(fraud_idx)), replace=False)
    l_sample = rng.choice(legit_idx, min(half, len(legit_idx)), replace=False)
    idx = np.concatenate([f_sample, l_sample])
    rng.shuffle(idx)

    print(f"[data] Quantum subset: {len(idx)} samples "
          f"(fraud={len(f_sample)}, legit={len(l_sample)})")
    return X[idx], y[idx]


# ── Main pipeline ──────────────────────────────────────────────────────────────

def _process_split(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering, encoding, and column dropping to one split."""
    df = engineer_features(df)
    df = clean_and_drop(df)
    df = encode_categoricals(df)
    return df


def prepare_data(random_state: int = config.RANDOM_STATE) -> dict:
    """
    End-to-end pipeline returning a dict with keys:
      X_train, X_test, y_train, y_test           – scaled, full
      X_train_bal, y_train_bal                    – undersampled for classical
      X_quantum, y_quantum                        – small balanced for quantum
      feature_names, scaler
    """
    df_train, df_test = load_dataset()

    # Process both splits identically
    df_train = _process_split(df_train)
    df_test = _process_split(df_test)

    # Align columns (in case encoding differs slightly)
    common_cols = sorted(set(df_train.columns) & set(df_test.columns))
    common_cols = [c for c in common_cols if c != config.TARGET_COLUMN]
    target = config.TARGET_COLUMN

    X_train_raw = df_train[common_cols].values
    y_train = df_train[target].values
    X_test_raw = df_test[common_cols].values
    y_test = df_test[target].values
    feature_names = common_cols

    print(f"[data] Final feature count: {len(feature_names)}")
    print(f"[data] Train shape: {X_train_raw.shape}, Test shape: {X_test_raw.shape}")

    # Scale to [-1, 1]
    X_train_sc, X_test_sc, scaler = scale_features(X_train_raw, X_test_raw)

    # Balanced subsets
    X_train_bal, y_train_bal = undersample(X_train_sc, y_train, random_state=random_state)
    X_quantum, y_quantum = create_quantum_subset(X_train_sc, y_train, random_state=random_state)

    return dict(
        X_train=X_train_sc, X_test=X_test_sc,
        y_train=y_train, y_test=y_test,
        X_train_bal=X_train_bal, y_train_bal=y_train_bal,
        X_quantum=X_quantum, y_quantum=y_quantum,
        feature_names=feature_names,
        scaler=scaler,
    )
