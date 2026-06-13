
# 🌿 EcoTrack AI — Carbon Intelligence Platform

> AI-powered carbon footprint calculator with ML predictions, Groq AI insights,
> anomaly detection and EcoBot carbon coach.
> **Hack2Skill Challenge 3** submission.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/tests-43%20passing-brightgreen)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**🔗 Live Demo**: https://ecotracka-i.netlify.app
**⚙️ Backend API**: https://aaricacoding-ecotrack-ai.hf.space

---

## What It Does

| Feature | Detail |
|---|---|
| **4-Step Wizard** | Transport · Home Energy · Diet · Shopping |
| **ML Forecast** | Polynomial Ridge Regression — 6-month carbon trajectory |
| **Anomaly Detection** | Isolation Forest detects unusual emission spikes |
| **AI Insights** | Groq LLaMA generates personalised footprint analysis |
| **EcoBot** | Multi-turn AI carbon coach powered by Groq |
| **Smart Dashboard** | Charts · comparison bars vs global/India benchmarks |
| **Ranked Tips** | Actions sorted by CO₂ impact — highest savings first |
| **Secure Accounts** | JWT + bcrypt authentication |

---

## Architecture

```
ecotrack-ai/
├── backend/
│   ├── app/
│   │   ├── core/        # config · security · database
│   │   ├── models/      # Pydantic schemas · SQLAlchemy ORM
│   │   ├── routers/     # auth · carbon · predictions · tips · insights
│   │   ├── services/    # carbon_calculator · ml_predictor · ai_insights · anomaly_detector
│   │   └── main.py      # FastAPI app · middleware · security headers
│   ├── tests/
│   │   └── test_all.py  # 43 deterministic unit tests
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html       # Single-file SPA · Chart.js · ARIA compliant
```

---

## Quick Start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

```bash
pytest tests/ -v --tb=short
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and receive JWT |
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

### Polynomial Ridge Regression
- `PolynomialFeatures(degree=2)` + `Ridge(alpha=1.0, random_state=42)`
- Captures realistic reduction curve — rapid early gains then plateau
- Falls back to simulated history when user has fewer than 3 records

### Isolation Forest
- `IsolationForest(n_estimators=100, contamination=0.15, random_state=42)`
- Trains on user's personal history — not global thresholds
- Returns per-category z-scores + human-readable explanation

---

## Security

| Layer | Mechanism |
|---|---|
| Passwords | bcrypt via passlib |
| Auth | HS256 JWT · 60-minute expiry |
| Validation | Pydantic v2 strict schemas |
| Rate limiting | slowapi · 5 reg/min · 10 login/min · 30 calc/min |
| Headers | X-Frame-Options · HSTS · X-Content-Type-Options |
| Secrets | Environment variables only · never hardcoded |

---

## Tests — 43 Passing

| Class | Coverage |
|---|---|
| `TestTransportCalculation` | Zero input · petrol vs EV · flights |
| `TestHomeCalculation` | Solar · per-capita scaling |
| `TestDietCalculation` | Vegan vs omnivore · waste multiplier |
| `TestRatingAndPercentile` | All 5 tiers · monotonicity · bounds |
| `TestFullFootprint` | Total integrity · valid rating |
| `TestMLPrediction` | Determinism · output length · non-negative |
| `TestInputValidation` | Negative values · invalid enums |
| `TestSecurity` | bcrypt · JWT roundtrip · tampered token |
| `TestAnomalyDetection` | Spike detection · z-scores · determinism |
| `TestInsightSchemas` | AI request/response validation |

---

## Emission Factors

| Category | Factor | Source |
|---|---|---|
| Petrol car | 0.192 kg CO₂e/km | EPA 2023 |
| EV India grid | 0.053 kg CO₂e/km | CEA 2023 |
| Electricity India | 0.716 kg CO₂e/kWh | CEA 2023 |
| Short-haul flight | 255 kg CO₂e/trip | ICAO |
| Long-haul flight | 1050 kg CO₂e/trip | ICAO |
| Vegan diet | 1500 kg CO₂e/yr | Poore & Nemecek 2018 |
| Global average | 4000 kg CO₂e/yr | IPCC AR6 |
| India average | 1800 kg CO₂e/yr | World Bank |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI · Python 3.11 · Uvicorn |
| Database | SQLAlchemy · SQLite |
| ML | scikit-learn · numpy |
| AI | Groq LLaMA 3.1 8B |
| Auth | python-jose · passlib bcrypt |
| Frontend | Vanilla JS · Chart.js |
| Deployment | HuggingFace Spaces · Netlify |
| Testing | pytest · 43 tests |

---

## License

MIT License : Built for Hack2Skill Challenge 3
