---
title: EcoTrack AI
emoji: 🌿
colorFrom: green
colorTo: green
sdk: docker
pinned: false
---

# EcoTrack AI : Carbon Intelligence Platform

> AI-powered carbon footprint calculator with ML predictions, Groq AI insights, anomaly detection and EcoBot coach.
> **Hack2Skill Challenge 3** submission.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/tests-43%20passing-brightgreen)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

🔗 **Live Demo**: https://ecotracka-i.netlify.app
💻 **Backend API**: https://aaricacoding-ecotrack-ai.hf.space

---

## What It Does

EcoTrack AI turns abstract environmental data into personal, actionable intelligence:

| Feature | Detail |
|---|---|
| **4-Step Wizard** | Transport · Home Energy · Diet · Shopping — under 2 minutes |
| **ML Forecast** | Polynomial Ridge Regression predicts your 6-month carbon trajectory |
| **Anomaly Detection** | Isolation Forest detects unusual emission spikes in your history |
| **AI Insights** | Groq LLaMA generates personalised narrative analysis of your footprint |
| **EcoBot** | Multi-turn AI carbon coach — knows your exact footprint data |
| **Smart Dashboard** | Donut chart, comparison bars vs global/India benchmarks, trend chart |
| **Ranked Tips** | Personalised actions sorted by CO₂ impact — highest savings first |
| **Secure Accounts** | JWT authentication + bcrypt hashing for persistent history tracking |

---

## Architecture

```
ecotrack-ai/
├── backend/
│   ├── app/
│   │   ├── core/           # config.py · security.py · database.py
│   │   ├── models/         # schemas.py (Pydantic) · db_models.py (SQLAlchemy)
│   │   ├── routers/        # auth · carbon · predictions · tips · insights
│   │   ├── services/       # carbon_calculator · ml_predictor · ai_insights · anomaly_detector
│   │   └── main.py         # FastAPI app, middleware, security headers, lifespan
│   ├── tests/
│   │   └── test_all.py     # 43 deterministic unit tests
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html          # Single-file SPA (Chart.js, dark eco theme, ARIA compliant)
```

---

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set SECRET_KEY and GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
open frontend/index.html
```

### Run Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user account |
| POST | `/api/auth/login` | Login and receive JWT token |
| GET | `/api/auth/me` | Get current user profile |
| POST | `/api/carbon/calculate` | Calculate footprint (authenticated) |
| POST | `/api/carbon/calculate/anonymous` | Calculate footprint (no auth) |
| GET | `/api/carbon/history` | Get user calculation history |
| POST | `/api/predictions/forecast` | 6-month ML forecast |
| POST | `/api/tips/personalized` | Get ranked reduction tips |
| POST | `/api/insights/analyze` | AI-powered footprint analysis |
| POST | `/api/insights/anomaly` | Isolation Forest anomaly detection |
| POST | `/api/insights/chat` | EcoBot multi-turn conversation |
| GET | `/health` | Health check |

---

## ML Models

### 1. Polynomial Ridge Regression (Trend Forecasting)
- **Algorithm**: `PolynomialFeatures(degree=2)` + `Ridge(alpha=1.0)`
- **Why degree 2**: Captures the realistic "easy wins first, then plateau" reduction curve
- **Why Ridge**: L2 regularisation prevents overfitting on small historical datasets
- **Determinism**: Fixed `random_state=42` — tests never flake

### 2. Isolation Forest (Anomaly Detection)
- **Algorithm**: `IsolationForest(n_estimators=100, contamination=0.15)`
- **Input**: User's personal 6-month emission history (4 categories)
- **Output**: Per-category z-scores + human-readable explanation
- **Why this matters**: Detects multivariate anomalies — unusual combinations across categories, not just single-category spikes

---

## Security

| Layer | Mechanism |
|---|---|
| Password storage | bcrypt via passlib (random salt per hash) |
| Authentication | HS256 JWT, 60-minute expiry |
| Input validation | Pydantic v2 strict schemas |
| Rate limiting | slowapi per-IP: 5 reg/min, 10 login/min, 30 calc/min |
| CORS | Configurable allowlist from environment variables |
| Response headers | X-Frame-Options, HSTS, X-Content-Type-Options |
| Secrets | All via `.env` — never hardcoded, excluded from git |

---

## Testing — 43 Tests, 10 Classes

| Test Class | What It Covers |
|---|---|
| `TestTransportCalculation` | Zero input, petrol vs EV, flight emissions |
| `TestHomeCalculation` | Solar reduction, per-capita scaling |
| `TestDietCalculation` | Vegan vs omnivore, waste multiplier |
| `TestRatingAndPercentile` | All 5 tiers, monotonicity, bounds |
| `TestFullFootprint` | Total = sum of parts, valid rating |
| `TestMLPrediction` | Determinism, output length, non-negative |
| `TestInputValidation` | Negative values, invalid enums, out-of-range |
| `TestSecurity` | bcrypt hashing, JWT roundtrip, tampered token |
| `TestAnomalyDetection` | Spike detection, z-scores, determinism |
| `TestInsightSchemas` | AI request/response validation |

---

## Emission Factor Sources

| Category | Factor | Source |
|---|---|---|
| Petrol car | 0.192 kg CO₂e/km | EPA 2023 |
| EV (India grid) | 0.053 kg CO₂e/km | CEA 2023 |
| Electricity (India) | 0.716 kg CO₂e/kWh | CEA 2023 |
| Short-haul flight | 255 kg CO₂e/trip | ICAO |
| Long-haul flight | 1050 kg CO₂e/trip | ICAO |
| Vegan diet baseline | 1500 kg CO₂e/yr | Poore & Nemecek 2018 |
| Global average | 4000 kg CO₂e/yr | IPCC AR6 |
| India average | 1800 kg CO₂e/yr | World Bank |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Database | SQLAlchemy + SQLite |
| ML | scikit-learn, numpy |
| AI | Groq LLaMA 3.1 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Rate Limiting | slowapi |
| Frontend | Vanilla JS, Chart.js |
| Deployment | HuggingFace Spaces (backend), Netlify (frontend) |
| Testing | pytest, 43 tests |

---

## License

MIT License  
*Built for Hack2Skill Challenge 3 · Carbon Footprint Awareness Platform*
