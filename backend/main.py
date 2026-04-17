"""
FastAPI Backend for Fraud Detection System

Main API server that serves predictions and model information.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transaction_processor import (
    TransactionProcessor,
    identify_risk_factors,
    get_risk_level,
    generate_recommendation
)
from src.models.classical_models import ClassicalModel
from src.models.quantum_models import QSVMModel
from src.models.ensemble import WeightedEnsemble
import config

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
mongodb_client: Optional[AsyncIOMotorClient] = None
database = None


# ── Initialize FastAPI ─────────────────────────────────────────────────────

app = FastAPI(
    title="Quantum-Classical Fraud Detection API",
    description="Real-time fraud detection using hybrid quantum-classical ML",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ────────────────────────────────────────────────────────

class TransactionInput(BaseModel):
    """User input from the live transaction checker form."""
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    merchant: str = Field(..., description="Merchant name")
    category: str = Field(..., description="Transaction category")
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    time: str = Field(..., description="Transaction time (HH:MM)")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    gender: Literal["M", "F"] = Field(..., description="Customer gender")
    job: str = Field(..., description="Customer job category")
    customer_city: str = Field(..., description="Customer home city")
    customer_state: str = Field(..., description="Customer home state (2-letter)")
    transaction_city: str = Field(..., description="Transaction city")
    transaction_state: str = Field(..., description="Transaction state (2-letter)")

    class Config:
        schema_extra = {
            "example": {
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
        }


class ModelPrediction(BaseModel):
    """Individual model prediction."""
    score: float = Field(..., description="Fraud probability (0-100)")
    decision: str = Field(..., description="FRAUD or SAFE")


class RiskFactor(BaseModel):
    """Individual risk factor."""
    level: str = Field(..., description="LOW, MEDIUM, HIGH")
    factor: str = Field(..., description="Risk factor name")
    detail: str = Field(..., description="Detailed explanation")


class PredictionOutput(BaseModel):
    """Complete prediction response."""
    ensemble_score: float = Field(..., description="Final fraud probability (0-100)")
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    recommendation: str = Field(..., description="Action recommendation")

    models: Dict[str, ModelPrediction] = Field(..., description="Individual model predictions")
    risk_factors: List[RiskFactor] = Field(..., description="Identified risk factors")
    feature_values: Dict[str, float] = Field(..., description="Engineered feature values")


# ── Global State (Loaded Models) ───────────────────────────────────────────

class ModelCache:
    """Cache for loaded ML models."""
    def __init__(self):
        self.classical_model = None
        self.quantum_model = None
        self.ensemble_weight = 0.5
        self.processor = None
        self.loaded = False

    def load_models(self):
        """Load trained models from disk."""
        try:
            print("[API] Loading trained models...")

            # Load saved models (you'll need to save these during training)
            models_dir = config.RESULTS_DIR / "models"
            models_dir.mkdir(exist_ok=True)

            # For now, we'll create dummy models
            # In production, load real trained models:
            # self.classical_model = joblib.load(models_dir / "xgboost.pkl")
            # self.quantum_model = joblib.load(models_dir / "qsvm.pkl")

            print("[API] ⚠️  Using mock models (train and save real models first)")

            # Create processor with selected features
            # These should match your actual training results
            all_features = [
                "amt", "merchant", "category", "hour", "day_of_week",
                "month", "age", "gender", "job", "lat", "long",
                "merch_lat", "merch_long", "distance", "lat_diff",
                "long_diff", "city_pop"
            ]
            selected_features = ["amt", "distance", "hour", "category", "age", "merchant"]

            self.processor = TransactionProcessor(all_features, selected_features)
            self.loaded = True

            print("[API] ✓ Models loaded successfully")

        except Exception as e:
            print(f"[API] ✗ Error loading models: {e}")
            raise


# Initialize cache
model_cache = ModelCache()


# ── API Endpoints ──────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Load models and connect to MongoDB when API starts."""
    global mongodb_client, database

    # Load ML models
    model_cache.load_models()

    # Connect to MongoDB
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        database = mongodb_client.fraud_detection
        print("[MongoDB] Connected successfully")
    except Exception as e:
        print(f"[MongoDB] Connection failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("[MongoDB] Connection closed")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Fraud Detection API",
        "status": "running",
        "models_loaded": model_cache.loaded
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy" if model_cache.loaded else "not ready",
        "models": {
            "classical": model_cache.classical_model is not None,
            "quantum": model_cache.quantum_model is not None,
            "processor": model_cache.processor is not None
        }
    }


@app.post("/api/predict/transaction", response_model=PredictionOutput)
async def predict_fraud(transaction: TransactionInput):
    """
    Predict fraud probability for a live transaction.

    This endpoint:
    1. Engineers features from user input
    2. Runs predictions through all models
    3. Identifies risk factors
    4. Returns comprehensive fraud assessment
    """
    if not model_cache.loaded:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please train models first."
        )

    try:
        # Convert to dict for processing
        user_input = transaction.dict()

        # Step 1: Process transaction to get features
        scaled_features = model_cache.processor.process_transaction(user_input)
        engineered_features = model_cache.processor.get_feature_dict(user_input)

        # Step 2: Get predictions from models
        # NOTE: For demo, we'll generate realistic mock predictions
        # In production, use real models:
        # classical_proba = model_cache.classical_model.predict_proba(scaled_features)[0, 1]
        # quantum_proba = model_cache.quantum_model.predict_proba(scaled_features)[0, 1]

        classical_proba, quantum_proba, ensemble_proba = _generate_mock_prediction(
            user_input, engineered_features
        )

        # Step 3: Determine risk level
        risk_level = get_risk_level(ensemble_proba)

        # Step 4: Identify risk factors
        risk_factors = identify_risk_factors(user_input, engineered_features)

        # Step 5: Generate recommendation
        recommendation = generate_recommendation(risk_level, risk_factors)

        # Build response
        response = PredictionOutput(
            ensemble_score=round(ensemble_proba * 100, 2),
            risk_level=risk_level,
            recommendation=recommendation,
            models={
                "classical": ModelPrediction(
                    score=round(classical_proba * 100, 2),
                    decision="FRAUD" if classical_proba > 0.5 else "SAFE"
                ),
                "quantum": ModelPrediction(
                    score=round(quantum_proba * 100, 2),
                    decision="FRAUD" if quantum_proba > 0.5 else "SAFE"
                ),
                "ensemble": ModelPrediction(
                    score=round(ensemble_proba * 100, 2),
                    decision="FRAUD" if ensemble_proba > 0.5 else "SAFE"
                )
            },
            risk_factors=[
                RiskFactor(**rf) for rf in risk_factors
            ],
            feature_values={
                k: round(v, 2) for k, v in engineered_features.items()
            }
        )

        # Save prediction to MongoDB
        if database is not None:
            try:
                await database.predictions.insert_one({
                    "transaction": user_input,
                    "result": response.dict(),
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                print(f"[MongoDB] Failed to save prediction: {e}")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


def _generate_mock_prediction(user_input: Dict, features: Dict) -> tuple[float, float, float]:
    """
    Generate realistic mock predictions based on risk factors.

    Replace this with real model predictions in production.
    """
    # Start with base probability
    base_prob = 0.1

    # Adjust based on amount
    if user_input["amount"] > 2000:
        base_prob += 0.3
    elif user_input["amount"] > 1000:
        base_prob += 0.2
    elif user_input["amount"] > 500:
        base_prob += 0.1

    # Adjust based on distance
    distance = features["distance"]
    if distance > 200:
        base_prob += 0.25
    elif distance > 100:
        base_prob += 0.15
    elif distance > 50:
        base_prob += 0.08

    # Adjust based on time
    hour = features["hour"]
    if hour < 6 or hour >= 23:
        base_prob += 0.15

    # Adjust based on category
    if user_input["category"] in ["shopping_net", "misc_net"]:
        base_prob += 0.1

    # Adjust based on merchant
    if user_input["merchant"] == "Unknown":
        base_prob += 0.15

    # Cap at 0.95
    base_prob = min(base_prob, 0.95)

    # Add some variance for different models
    classical = np.clip(base_prob - 0.05, 0.0, 1.0)
    quantum = np.clip(base_prob + 0.08, 0.0, 1.0)
    ensemble = np.clip((classical + quantum) / 2, 0.0, 1.0)

    return classical, quantum, ensemble


@app.get("/api/options/merchants")
async def get_merchants():
    """Get list of available merchants."""
    return {
        "merchants": [
            "Walmart", "Amazon", "Target", "Costco", "Shell",
            "Chevron", "Starbucks", "McDonald's", "Subway",
            "Best Buy", "Home Depot", "Unknown"
        ]
    }


@app.get("/api/options/categories")
async def get_categories():
    """Get list of transaction categories."""
    return {
        "categories": [
            {"value": "grocery_pos", "label": "Grocery Store"},
            {"value": "gas_transport", "label": "Gas & Transportation"},
            {"value": "shopping_net", "label": "Online Shopping"},
            {"value": "shopping_pos", "label": "In-Store Shopping"},
            {"value": "food_dining", "label": "Food & Dining"},
            {"value": "entertainment", "label": "Entertainment"},
            {"value": "personal_care", "label": "Personal Care"},
            {"value": "health_fitness", "label": "Health & Fitness"},
            {"value": "travel", "label": "Travel"},
            {"value": "misc_pos", "label": "Miscellaneous (In-Store)"},
            {"value": "misc_net", "label": "Miscellaneous (Online)"},
            {"value": "home", "label": "Home & Garden"}
        ]
    }


@app.get("/api/options/jobs")
async def get_jobs():
    """Get list of job categories."""
    return {
        "jobs": [
            "Sales", "Engineer", "Teacher", "Healthcare",
            "Retail", "Manager", "Technician", "Driver",
            "Consultant", "Self-employed", "Student", "Other"
        ]
    }


@app.get("/api/history")
async def get_prediction_history(limit: int = 10):
    """Get recent prediction history from database."""
    if database is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        cursor = database.predictions.find().sort("timestamp", -1).limit(limit)
        predictions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            predictions.append(doc)
        return {"predictions": predictions, "count": len(predictions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@app.get("/api/presets")
async def get_preset_transactions():
    """Get preset transaction scenarios for quick testing."""
    return {
        "presets": {
            "normal": {
                "name": "Normal Transaction",
                "description": "Typical safe transaction",
                "data": {
                    "amount": 45.50,
                    "merchant": "Starbucks",
                    "category": "food_dining",
                    "time": "08:30",
                    "age": 32,
                    "gender": "F",
                    "job": "Engineer"
                }
            },
            "suspicious_large": {
                "name": "Suspicious Large Amount",
                "description": "High-value transaction at unknown merchant",
                "data": {
                    "amount": 4567.89,
                    "merchant": "Unknown",
                    "category": "shopping_net",
                    "time": "23:45",
                    "age": 28,
                    "gender": "M",
                    "job": "Sales"
                }
            },
            "unusual_location": {
                "name": "Unusual Location",
                "description": "Transaction far from home",
                "data": {
                    "amount": 890.00,
                    "merchant": "Best Buy",
                    "category": "shopping_pos",
                    "time": "14:20",
                    "age": 45,
                    "gender": "F",
                    "job": "Teacher"
                }
            },
            "late_night_online": {
                "name": "Late Night Online",
                "description": "Late night online purchase",
                "data": {
                    "amount": 1299.99,
                    "merchant": "Amazon",
                    "category": "shopping_net",
                    "time": "03:15",
                    "age": 38,
                    "gender": "M",
                    "job": "Healthcare"
                }
            }
        }
    }


# ── Run Server ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
