"""
Transaction Processor - Convert live user inputs to model-ready features.

This module bridges the gap between user-friendly form inputs and the
feature vectors expected by trained ML models.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List
import joblib
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ── Lookup Tables ──────────────────────────────────────────────────────────

# Merchant categories (from training data)
MERCHANT_MAPPING = {
    "Walmart": 0, "Amazon": 1, "Target": 2, "Costco": 3,
    "Shell": 4, "Chevron": 5, "Starbucks": 6, "McDonald's": 7,
    "Subway": 8, "Best Buy": 9, "Home Depot": 10, "Unknown": 11,
}

CATEGORY_MAPPING = {
    "grocery_pos": 0, "gas_transport": 1, "shopping_net": 2,
    "shopping_pos": 3, "food_dining": 4, "entertainment": 5,
    "personal_care": 6, "health_fitness": 7, "travel": 8,
    "misc_pos": 9, "misc_net": 10, "home": 11
}

JOB_MAPPING = {
    "Sales": 0, "Engineer": 1, "Teacher": 2, "Healthcare": 3,
    "Retail": 4, "Manager": 5, "Technician": 6, "Driver": 7,
    "Consultant": 8, "Self-employed": 9, "Student": 10, "Other": 11
}

# Major US cities coordinates (add more as needed)
CITY_COORDINATES = {
    ("New York", "NY"): (40.7128, -74.0060),
    ("Los Angeles", "CA"): (34.0522, -118.2437),
    ("Chicago", "IL"): (41.8781, -87.6298),
    ("Houston", "TX"): (29.7604, -95.3698),
    ("Phoenix", "AZ"): (33.4484, -112.0740),
    ("Philadelphia", "PA"): (39.9526, -75.1652),
    ("San Antonio", "TX"): (29.4241, -98.4936),
    ("San Diego", "CA"): (32.7157, -117.1611),
    ("Dallas", "TX"): (32.7767, -96.7970),
    ("San Jose", "CA"): (37.3382, -121.8863),
    ("Austin", "TX"): (30.2672, -97.7431),
    ("Jacksonville", "FL"): (30.3322, -81.6557),
    ("Fort Worth", "TX"): (32.7555, -97.3308),
    ("Columbus", "OH"): (39.9612, -82.9988),
    ("Charlotte", "NC"): (35.2271, -80.8431),
    ("San Francisco", "CA"): (37.7749, -122.4194),
    ("Indianapolis", "IN"): (39.7684, -86.1581),
    ("Seattle", "WA"): (47.6062, -122.3321),
    ("Denver", "CO"): (39.7392, -104.9903),
    ("Boston", "MA"): (42.3601, -71.0589),
    ("Miami", "FL"): (25.7617, -80.1918),
    ("Atlanta", "GA"): (33.7490, -84.3880),
    ("Detroit", "MI"): (42.3314, -83.0458),
    ("Las Vegas", "NV"): (36.1699, -115.1398),
}

CITY_POPULATION = {
    ("New York", "NY"): 8000000,
    ("Los Angeles", "CA"): 4000000,
    ("Chicago", "IL"): 2700000,
    ("Houston", "TX"): 2300000,
    ("Phoenix", "AZ"): 1600000,
    # ... simplified, add more or default to average
}


# ── Helper Functions ───────────────────────────────────────────────────────

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (in miles)."""
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    miles = 3956 * c  # Radius of earth in miles
    return miles


def get_coordinates(city: str, state: str) -> tuple[float, float]:
    """Get lat/long for a city, or return default if not found."""
    key = (city, state)
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]
    # Default to US center if city not found
    return (39.8283, -98.5795)  # Geographic center of US


def get_population(city: str, state: str) -> int:
    """Get population for a city, or return average if not found."""
    key = (city, state)
    return CITY_POPULATION.get(key, 500000)  # Default to medium city


# ── Main Processing Class ──────────────────────────────────────────────────

class TransactionProcessor:
    """
    Converts user transaction inputs into model-ready feature vectors.

    This class handles:
    1. Feature engineering from raw inputs
    2. Feature selection (keeping only the features used by models)
    3. Scaling using the saved scaler from training
    """

    def __init__(self, feature_names: List[str], selected_features: List[str]):
        """
        Parameters
        ----------
        feature_names : All feature names from training (in order)
        selected_features : The subset selected by two-step FS
        """
        self.all_feature_names = feature_names
        self.selected_features = selected_features
        self.selected_indices = [
            feature_names.index(f) for f in selected_features
        ]

        # Load the scaler used during training
        scaler_path = config.RESULTS_DIR / "scaler.pkl"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
        else:
            print("[WARNING] Scaler not found, predictions may be inaccurate!")
            from sklearn.preprocessing import MinMaxScaler
            self.scaler = MinMaxScaler(feature_range=(-1, 1))

    def process_transaction(self, user_input: Dict) -> np.ndarray:
        """
        Convert user input dict to scaled feature vector.

        Parameters
        ----------
        user_input : dict with keys:
            - amount, merchant, category
            - date, time
            - age, gender, job
            - customer_city, customer_state
            - transaction_city, transaction_state

        Returns
        -------
        np.ndarray of shape (1, n_selected_features) ready for prediction
        """
        # Step 1: Engineer all features
        all_features = self._engineer_all_features(user_input)

        # Step 2: Select only the features used by models
        selected_values = [all_features[name] for name in self.selected_features]

        # Step 3: Convert to numpy array
        feature_vector = np.array(selected_values).reshape(1, -1)

        # Step 4: Scale using training scaler
        scaled = self.scaler.transform(feature_vector)

        return scaled

    def _engineer_all_features(self, user_input: Dict) -> Dict[str, float]:
        """
        Create all engineered features matching training pipeline.

        Returns dict with feature_name → value
        """
        features = {}

        # ── Basic transaction info ────────────────────────────────
        features["amt"] = float(user_input["amount"])
        features["merchant"] = MERCHANT_MAPPING.get(
            user_input["merchant"],
            len(MERCHANT_MAPPING)  # Unknown merchants get highest code
        )
        features["category"] = CATEGORY_MAPPING.get(
            user_input["category"], 0
        )

        # ── Time features ──────────────────────────────────────────
        dt = datetime.fromisoformat(f"{user_input['date']} {user_input['time']}")
        features["hour"] = dt.hour
        features["day_of_week"] = dt.weekday()  # 0=Monday, 6=Sunday
        features["month"] = dt.month

        # ── Customer features ──────────────────────────────────────
        features["age"] = float(user_input["age"])
        features["gender"] = 1 if user_input["gender"] == "F" else 0
        features["job"] = JOB_MAPPING.get(user_input["job"], 11)

        # ── Location features ──────────────────────────────────────
        cust_city = user_input["customer_city"]
        cust_state = user_input["customer_state"]
        trans_city = user_input["transaction_city"]
        trans_state = user_input["transaction_state"]

        cust_lat, cust_long = get_coordinates(cust_city, cust_state)
        trans_lat, trans_long = get_coordinates(trans_city, trans_state)

        features["lat"] = cust_lat
        features["long"] = cust_long
        features["merch_lat"] = trans_lat
        features["merch_long"] = trans_long

        # Distance calculations
        distance = calculate_distance(cust_lat, cust_long, trans_lat, trans_long)
        features["distance"] = distance
        features["lat_diff"] = abs(cust_lat - trans_lat)
        features["long_diff"] = abs(cust_long - trans_long)

        # Population (if in feature set)
        features["city_pop"] = float(get_population(cust_city, cust_state))

        # ── State encoding (if needed) ─────────────────────────────
        # You can add state encoding here if your model uses it
        # For now, we'll skip as it's not in the main selected features

        return features

    def get_feature_dict(self, user_input: Dict) -> Dict[str, float]:
        """
        Get all engineered features as dict (useful for explanations).
        """
        return self._engineer_all_features(user_input)


# ── Risk Analysis Functions ────────────────────────────────────────────────

def identify_risk_factors(user_input: Dict, engineered_features: Dict) -> List[Dict]:
    """
    Analyze transaction and identify specific risk factors.

    Returns list of dicts with keys: level, factor, detail
    """
    risk_factors = []

    # Risk Factor 1: High transaction amount
    amount = user_input["amount"]
    if amount > 1000:
        level = "HIGH" if amount > 2000 else "MEDIUM"
        risk_factors.append({
            "level": level,
            "factor": "Unusual transaction amount",
            "detail": f"${amount:.2f} is significantly above average ($120)"
        })

    # Risk Factor 2: Large distance from home
    distance = engineered_features["distance"]
    if distance > 50:
        level = "HIGH" if distance > 200 else "MEDIUM"
        risk_factors.append({
            "level": level,
            "factor": "Large distance from home",
            "detail": f"{distance:.0f} miles from registered address"
        })

    # Risk Factor 3: Unusual time
    hour = engineered_features["hour"]
    if hour < 6 or hour >= 23:
        risk_factors.append({
            "level": "MEDIUM",
            "factor": "Unusual transaction time",
            "detail": f"Transaction at {hour}:00 (late night/early morning)"
        })

    # Risk Factor 4: Online shopping with high amount
    if user_input["category"] in ["shopping_net", "misc_net"] and amount > 500:
        risk_factors.append({
            "level": "HIGH",
            "factor": "High-value online purchase",
            "detail": "Large online transactions have higher fraud rates"
        })

    # Risk Factor 5: Unknown merchant
    if user_input["merchant"] == "Unknown":
        risk_factors.append({
            "level": "MEDIUM",
            "factor": "Unrecognized merchant",
            "detail": "Transaction at unknown or new merchant"
        })

    # Positive Factor: Recognized merchant near home
    if distance < 10 and user_input["merchant"] in ["Walmart", "Target", "Costco"]:
        risk_factors.append({
            "level": "LOW",
            "factor": "Recognized merchant near home",
            "detail": "Transaction pattern matches typical behavior"
        })

    return risk_factors


def get_risk_level(fraud_probability: float) -> str:
    """Map fraud probability [0-1] to risk level."""
    if fraud_probability < 0.3:
        return "LOW"
    elif fraud_probability < 0.6:
        return "MEDIUM"
    elif fraud_probability < 0.85:
        return "HIGH"
    else:
        return "CRITICAL"


def generate_recommendation(risk_level: str, risk_factors: List[Dict]) -> str:
    """Generate action recommendation based on risk assessment."""
    recommendations = {
        "LOW": "✅ APPROVE TRANSACTION\n\nThis transaction appears safe. Standard processing recommended.",

        "MEDIUM": "⚠️ REQUEST VERIFICATION\n\nSuggested actions:\n• Send SMS OTP to customer\n• Verify with security question\n• Monitor for similar patterns",

        "HIGH": "🚫 HOLD FOR REVIEW\n\nSuggested actions:\n• Block transaction temporarily\n• Contact customer directly\n• Request additional documentation\n• Escalate to fraud team",

        "CRITICAL": "🚨 BLOCK TRANSACTION\n\nImmediate actions required:\n• Block transaction immediately\n• Flag account for investigation\n• Contact customer via verified channels\n• Freeze card temporarily"
    }

    return recommendations.get(risk_level, "Review required")


# ── Example Usage ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: Process a suspicious transaction

    # Assume we have final selected features from training
    selected_features = ["amt", "distance", "hour", "category", "age", "merchant"]
    all_features = ["amt", "merchant", "category", "hour", "day_of_week",
                    "month", "age", "gender", "job", "lat", "long",
                    "merch_lat", "merch_long", "distance", "lat_diff",
                    "long_diff", "city_pop"]

    processor = TransactionProcessor(all_features, selected_features)

    # User input from form
    transaction = {
        "amount": 2450.00,
        "merchant": "Unknown",
        "category": "shopping_net",
        "date": "2024-03-15",
        "time": "23:45",
        "age": 35,
        "gender": "M",
        "job": "Engineer",
        "customer_city": "New York",
        "customer_state": "NY",
        "transaction_city": "Los Angeles",
        "transaction_state": "CA"
    }

    # Process to model-ready features
    scaled_features = processor.process_transaction(transaction)
    print("Scaled features shape:", scaled_features.shape)
    print("Scaled features:", scaled_features)

    # Get engineered features for analysis
    engineered = processor.get_feature_dict(transaction)
    print("\nEngineered features:")
    for key, val in engineered.items():
        print(f"  {key}: {val}")

    # Identify risk factors
    risks = identify_risk_factors(transaction, engineered)
    print("\nRisk factors:")
    for risk in risks:
        print(f"  [{risk['level']}] {risk['factor']}: {risk['detail']}")
