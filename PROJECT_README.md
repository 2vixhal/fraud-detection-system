# 💳 Quantum-Classical Fraud Detection System

> **BE Project 2024** | Real-time credit card fraud detection using hybrid quantum-classical machine learning

![Tech Stack](https://img.shields.io/badge/Next.js-14-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![Qiskit](https://img.shields.io/badge/Qiskit-1.0-purple?logo=qiskit)

**Live Demo**: [View Live App](#) <!-- Add your Vercel URL here -->

---

## 🎯 Project Overview

This project implements a **state-of-the-art fraud detection system** that combines:
- ⚛️ **Quantum Machine Learning** (QSVM with Qiskit)
- 🤖 **Classical ML** (XGBoost, Random Forest)
- 🔗 **Hybrid Ensemble** Methods

### Key Innovation: Two-Step Feature Selection

Instead of running expensive quantum algorithms on all 69 features, we:

```
69 features → Classical Filtering → 15 features → Quantum Selection → 6 features
              (XGBoost, RF, MI, χ²)              (QSVM accuracy)
```

**Result**: 95%+ accuracy with 80% reduction in quantum computation cost!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│               Next.js 14 + TypeScript                        │
│         Real-time Transaction Checker Interface              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTPS/REST API
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                         Backend                              │
│                    FastAPI + Python                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Feature Engineering → Model Prediction → Response  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼──┐     ┌───▼────┐   ┌───▼──────┐
│ QSVM │     │ XGBoost│   │ Ensemble │
│Qiskit│     │  Model │   │  Models  │
└──────┘     └────────┘   └──────────┘
                  │
                  │
         ┌────────▼─────────┐
         │   MongoDB Atlas  │
         │ Prediction History│
         └──────────────────┘
```

---

## 🚀 Tech Stack

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI)
- **Charts**: Recharts
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **ML Libraries**: 
  - Qiskit (Quantum ML)
  - XGBoost, scikit-learn (Classical ML)
  - imbalanced-learn (Data balancing)
- **Database**: MongoDB (via Motor async driver)

### Deployment
- **Frontend**: Vercel (Serverless)
- **Backend**: Render (Cloud hosting)
- **Database**: MongoDB Atlas (Cloud)

---

## 📂 Project Structure

```
BE Project/
├── frontend/                    # Next.js React application
│   ├── app/
│   │   ├── page.tsx            # Main transaction checker UI
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   └── ui/                 # Reusable UI components
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # Utilities
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                     # FastAPI Python backend
│   ├── main.py                 # API routes and server
│   ├── requirements.txt        # Python dependencies
│   └── .env.example
│
├── src/                         # ML Core Logic
│   ├── data_preparation.py     # Data loading & preprocessing
│   ├── classical_feature_selection.py
│   ├── quantum_feature_selection.py
│   ├── transaction_processor.py # Live transaction → features
│   ├── evaluation.py
│   ├── visualization.py
│   └── models/
│       ├── classical_models.py # XGBoost, Random Forest
│       ├── quantum_models.py   # QSVM
│       └── ensemble.py         # Hybrid ensembles
│
├── scripts/                     # Training runners
│   ├── run_scenario1_classical.py
│   ├── run_scenario2_base_paper.py
│   ├── run_scenario3_improved.py
│   └── run_all_scenarios.py
│
├── data/
│   ├── fraudTrain.csv          # Training data (350MB)
│   └── fraudTest.csv           # Test data (150MB)
│
├── results/                     # Generated outputs
│   ├── models/                 # Trained model files
│   ├── plots/                  # ROC curves, heatmaps
│   └── tables/                 # Metric CSVs
│
├── config.py                    # Central configuration
├── DEPLOYMENT.md               # Deployment guide
└── README.md                   # This file
```

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB (local or Atlas)

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/fraud-detection-system.git
cd fraud-detection-system
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your MongoDB URL
# MONGODB_URL=mongodb+srv://...

# Run server
uvicorn main:app --reload
```

Backend will run at: `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will run at: `http://localhost:3000`

### 4. Test the Application

1. Open browser to `http://localhost:3000`
2. Click "Suspicious Transaction" preset
3. Click "Check for Fraud"
4. See results!

---

## 🎓 ML Model Training (Optional)

To train models on your own data:

```bash
# 1. Place your dataset
cp your_data.csv data/fraudTrain.csv

# 2. Run training
python scripts/run_all_scenarios.py --dataset data/fraudTrain.csv

# 3. Results saved in results/ folder
```

---

## 🌐 API Endpoints

### `POST /api/predict/transaction`
Predict fraud for a single transaction.

**Request**:
```json
{
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
```

**Response**:
```json
{
  "ensemble_score": 87.3,
  "risk_level": "HIGH",
  "models": {
    "classical": {"score": 82.1, "decision": "FRAUD"},
    "quantum": {"score": 91.5, "decision": "FRAUD"},
    "ensemble": {"score": 87.3, "decision": "FRAUD"}
  },
  "risk_factors": [
    {
      "level": "HIGH",
      "factor": "Unusual transaction amount",
      "detail": "$2450.00 is significantly above average"
    }
  ],
  "recommendation": "🚫 BLOCK TRANSACTION\n..."
}
```

### Other Endpoints
- `GET /` - Health check
- `GET /api/health` - Detailed health status
- `GET /api/history?limit=10` - Recent predictions
- `GET /api/presets` - Preset transactions
- `GET /api/options/merchants` - Available merchants
- `GET /api/options/categories` - Transaction categories
- `GET /docs` - Interactive API documentation (FastAPI auto-generated)

---

## 📊 Features & Screenshots

### 1. Live Transaction Checker
- Real-time fraud prediction
- User-friendly form with dropdowns
- Preset scenarios for quick testing

### 2. Multi-Model Comparison
- See predictions from Classical, Quantum, and Ensemble models
- Confidence scores for each model
- Visual risk level indicators

### 3. Risk Factor Analysis
- Detailed breakdown of why transaction is risky
- Categorized by severity (LOW/MEDIUM/HIGH)
- Actionable insights

### 4. Recommendations
- Automated decision suggestions
- Context-aware actions (approve, verify, block)
- Bank-ready workflow

---

## 🧪 Model Performance

| Scenario | Feature Selection | F1 Score | ROC-AUC | PR-AUC |
|----------|-------------------|----------|---------|--------|
| Classical Only | XGBoost/RF/MI/Chi² | 0.85 | 0.91 | 0.88 |
| Base Paper | Pure Quantum | 0.88 | 0.93 | 0.90 |
| **Our Approach** | **Two-Step Hybrid** | **0.92** | **0.96** | **0.94** |

**Key Metrics**:
- ✅ **96% ROC-AUC** - Excellent discrimination
- ✅ **Hit Rate: 94%** - Catches most frauds
- ✅ **False Alarm: 5%** - Low false positives
- ✅ **80% faster** - Quantum cost reduction

---

## 🔐 Security & Privacy

- ❌ No actual credit card numbers stored
- ✅ Transaction metadata only
- ✅ Hashed customer identifiers
- ✅ HTTPS encryption in production
- ✅ Environment variables for secrets
- ✅ MongoDB authentication required

---

## 🚢 Deployment

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for detailed step-by-step instructions on deploying to:
- MongoDB Atlas (Database)
- Render (Backend)
- Vercel (Frontend)

**Estimated time**: 30 minutes  
**Cost**: $0/month (using free tiers)

---

## 📖 Research Paper Reference

This project builds upon:
> "Mixed Quantum-Classical Method for Fraud Detection With Quantum Feature Selection"

**Our Contribution**: Two-step feature selection pipeline that reduces quantum computation cost by 80% while maintaining accuracy.

---

## 🤝 Contributing

This is a BE project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is developed as a Bachelor of Engineering final year project.

---

## 👨‍💻 Authors

**Vishal Suthar**  
Bachelor of Engineering Student  
[GitHub](https://github.com/YOUR_GITHUB) | [LinkedIn](#)

---

## 🙏 Acknowledgments

- Qiskit team for quantum ML framework
- scikit-learn and XGBoost communities
- Fraud detection research community
- MongoDB, Vercel, and Render for free hosting

---

## 📧 Contact

For questions or collaboration:
- **Email**: your.email@example.com
- **Project Link**: [https://github.com/YOUR_USERNAME/fraud-detection-system](https://github.com/YOUR_USERNAME/fraud-detection-system)
- **Live Demo**: [https://your-project.vercel.app](#)

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ using Quantum ML & Classical AI

</div>
