"""
Transaction Processor - Convert live user inputs to model-ready features.
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


MERCHANT_MAPPING = {
    "Walmart": 0, "Amazon": 1, "Target": 2, "Costco": 3,
    "Shell": 4, "Chevron": 5, "Starbucks": 6, "McDonald's": 7,
    "Subway": 8, "Best Buy": 9, "Home Depot": 10, "Unknown": 11,
    "Apple Store": 12, "Nike": 13, "Uber": 14, "Netflix": 15,
    "Spotify": 16, "Zara": 17, "IKEA": 18, "Whole Foods": 19,
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
    ("Portland", "OR"): (45.5152, -122.6784),
    ("Nashville", "TN"): (36.1627, -86.7816),
    ("Memphis", "TN"): (35.1495, -90.0490),
    ("Baltimore", "MD"): (39.2904, -76.6122),
    ("Milwaukee", "WI"): (43.0389, -87.9065),
    ("Albuquerque", "NM"): (35.0844, -106.6504),
    ("Tucson", "AZ"): (32.2226, -110.9747),
    ("Sacramento", "CA"): (38.5816, -121.4944),
    ("Kansas City", "MO"): (39.0997, -94.5786),
    ("Salt Lake City", "UT"): (40.7608, -111.8910),
    ("Raleigh", "NC"): (35.7796, -78.6382),
    ("Tampa", "FL"): (27.9506, -82.4572),
    ("Orlando", "FL"): (28.5383, -81.3792),
    ("Pittsburgh", "PA"): (40.4406, -79.9959),
    ("Minneapolis", "MN"): (44.9778, -93.2650),
    ("New Orleans", "LA"): (29.9511, -90.0715),
    # International cities (mapped to approx coordinates)
    ("Mumbai", "IN"): (19.0760, 72.8777),
    ("Delhi", "IN"): (28.7041, 77.1025),
    ("Bangalore", "IN"): (12.9716, 77.5946),
    ("London", "UK"): (51.5074, -0.1278),
    ("Toronto", "CA"): (43.6532, -79.3832),
    ("Sydney", "AU"): (-33.8688, 151.2093),
    ("Tokyo", "JP"): (35.6762, 139.6503),
    ("Berlin", "DE"): (52.5200, 13.4050),
    ("Paris", "FR"): (48.8566, 2.3522),
    ("Dubai", "AE"): (25.2048, 55.2708),
    ("Singapore", "SG"): (1.3521, 103.8198),
    ("Mexico City", "MX"): (19.4326, -99.1332),
    ("São Paulo", "BR"): (-23.5505, -46.6333),
}

CITY_POPULATION = {
    ("New York", "NY"): 8336817,
    ("Los Angeles", "CA"): 3979576,
    ("Chicago", "IL"): 2693976,
    ("Houston", "TX"): 2320268,
    ("Phoenix", "AZ"): 1680992,
    ("Philadelphia", "PA"): 1584064,
    ("San Antonio", "TX"): 1547253,
    ("San Diego", "CA"): 1423851,
    ("Dallas", "TX"): 1343573,
    ("San Jose", "CA"): 1021795,
    ("Austin", "TX"): 978908,
    ("San Francisco", "CA"): 873965,
    ("Seattle", "WA"): 737015,
    ("Denver", "CO"): 715522,
    ("Boston", "MA"): 675647,
    ("Miami", "FL"): 467963,
    ("Atlanta", "GA"): 498715,
    ("Las Vegas", "NV"): 641903,
}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, cos, sin, asin, sqrt
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    miles = 3956 * c
    return miles


def get_coordinates(city: str, state: str) -> tuple[float, float]:
    key = (city, state)
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]
    return (39.8283, -98.5795)


def get_population(city: str, state: str) -> int:
    key = (city, state)
    return CITY_POPULATION.get(key, 500000)


class TransactionProcessor:
    def __init__(self, feature_names: List[str], selected_features: List[str]):
        self.all_feature_names = feature_names
        self.selected_features = selected_features
        self.selected_indices = [
            feature_names.index(f) for f in selected_features
        ]

        scaler_path = config.MODELS_DIR / "scaler.pkl"
        if not scaler_path.exists():
            scaler_path = config.RESULTS_DIR / "scaler.pkl"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
        else:
            from sklearn.preprocessing import MinMaxScaler
            self.scaler = MinMaxScaler(feature_range=(-1, 1))

    def process_transaction(self, user_input: Dict) -> np.ndarray:
        all_features = self._engineer_all_features(user_input)
        selected_values = [all_features[name] for name in self.selected_features]
        feature_vector = np.array(selected_values).reshape(1, -1)
        scaled = self.scaler.transform(feature_vector)
        return scaled

    def _engineer_all_features(self, user_input: Dict) -> Dict[str, float]:
        features = {}

        features["amt"] = float(user_input["amount"])
        features["merchant"] = MERCHANT_MAPPING.get(
            user_input["merchant"],
            len(MERCHANT_MAPPING)
        )
        features["category"] = CATEGORY_MAPPING.get(
            user_input["category"], 0
        )

        dt = datetime.fromisoformat(f"{user_input['date']} {user_input['time']}")
        features["hour"] = dt.hour
        features["day_of_week"] = dt.weekday()
        features["month"] = dt.month

        features["age"] = float(user_input["age"])
        features["gender"] = 1 if user_input["gender"] == "F" else 0
        features["job"] = JOB_MAPPING.get(user_input["job"], 11)

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

        distance = calculate_distance(cust_lat, cust_long, trans_lat, trans_long)
        features["distance"] = distance
        features["lat_diff"] = abs(cust_lat - trans_lat)
        features["long_diff"] = abs(cust_long - trans_long)
        features["city_pop"] = float(get_population(cust_city, cust_state))

        return features

    def get_feature_dict(self, user_input: Dict) -> Dict[str, float]:
        return self._engineer_all_features(user_input)


def identify_risk_factors(user_input: Dict, engineered_features: Dict) -> List[Dict]:
    risk_factors = []

    amount = user_input["amount"]
    if amount > 2000:
        risk_factors.append({
            "level": "CRITICAL",
            "factor": "Very high transaction amount",
            "detail": f"${amount:.2f} is significantly above average spending ($120)"
        })
    elif amount > 1000:
        risk_factors.append({
            "level": "HIGH",
            "factor": "High transaction amount",
            "detail": f"${amount:.2f} is well above average spending ($120)"
        })
    elif amount > 500:
        risk_factors.append({
            "level": "MEDIUM",
            "factor": "Above average transaction amount",
            "detail": f"${amount:.2f} is above typical transaction amounts"
        })

    distance = engineered_features["distance"]
    if distance > 500:
        risk_factors.append({
            "level": "CRITICAL",
            "factor": "Extreme distance from home",
            "detail": f"{distance:.0f} miles from registered address — possible stolen card"
        })
    elif distance > 200:
        risk_factors.append({
            "level": "HIGH",
            "factor": "Large distance from home",
            "detail": f"{distance:.0f} miles from registered address"
        })
    elif distance > 50:
        risk_factors.append({
            "level": "MEDIUM",
            "factor": "Moderate distance from home",
            "detail": f"{distance:.0f} miles from registered address"
        })

    hour = engineered_features["hour"]
    if hour < 5 or hour >= 23:
        risk_factors.append({
            "level": "HIGH",
            "factor": "Late night / early morning transaction",
            "detail": f"Transaction at {hour:02d}:00 — high-risk time window"
        })
    elif hour < 6 or hour >= 22:
        risk_factors.append({
            "level": "MEDIUM",
            "factor": "Unusual transaction time",
            "detail": f"Transaction at {hour:02d}:00 — outside normal hours"
        })

    if user_input["category"] in ["shopping_net", "misc_net"] and amount > 500:
        risk_factors.append({
            "level": "HIGH",
            "factor": "High-value online purchase",
            "detail": "Large online transactions have higher fraud rates"
        })

    if user_input["merchant"] == "Unknown":
        risk_factors.append({
            "level": "HIGH",
            "factor": "Unrecognized merchant",
            "detail": "Transaction at unknown or unverified merchant"
        })

    if distance < 10 and user_input["merchant"] not in ["Unknown"] and amount < 200:
        risk_factors.append({
            "level": "LOW",
            "factor": "Local trusted transaction",
            "detail": "Small purchase at recognized merchant near home"
        })

    return risk_factors


def get_risk_level(fraud_probability: float) -> str:
    if fraud_probability < 0.25:
        return "LOW"
    elif fraud_probability < 0.55:
        return "MEDIUM"
    elif fraud_probability < 0.80:
        return "HIGH"
    else:
        return "CRITICAL"


def generate_recommendation(risk_level: str, risk_factors: List[Dict]) -> str:
    recommendations = {
        "LOW": "APPROVE TRANSACTION\n\nThis transaction appears safe and consistent with the customer's profile. Standard processing recommended.",
        "MEDIUM": "REQUEST VERIFICATION\n\nSuggested actions:\n• Send SMS/OTP verification to customer\n• Verify with security question\n• Monitor for similar patterns in next 24 hours",
        "HIGH": "HOLD FOR REVIEW\n\nSuggested actions:\n• Block transaction temporarily\n• Contact customer directly via verified phone\n• Request additional documentation\n• Escalate to fraud investigation team",
        "CRITICAL": "BLOCK TRANSACTION\n\nImmediate actions required:\n• Block transaction immediately\n• Flag account for investigation\n• Contact customer via verified channels\n• Freeze card temporarily\n• File suspicious activity report (SAR)"
    }
    return recommendations.get(risk_level, "Review required")
