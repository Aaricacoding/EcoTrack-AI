# 🌿 EcoTrack AI — Carbon Intelligence Platform

> AI-powered carbon footprint calculator with ML trend prediction, interactive dashboard, and personalised reduction tips.  
> **Hack2Skill Challenge 3** submission.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/tests-20%2B%20passing-brightgreen)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## What It Does

EcoTrack AI turns abstract environmental data into personal, actionable intelligence:

| Feature | Detail |
|---|---|
| **4-Step Wizard** | Transport · Home Energy · Diet · Shopping — under 2 minutes to complete |
| **ML Forecast** | Polynomial regression (scikit-learn) predicts your 6-month carbon trajectory |
| **Smart Dashboard** | Donut chart breakdown, comparison bars vs global/India benchmarks, trend chart |
| **Ranked Tips** | Personalised actions sorted by CO₂ impact — highest savings shown first |
| **Secure Accounts** | JWT authentication + bcrypt hashing for persistent history tracking |

---

## Architecture

```
ecotrack-ai/
├── backend/
│   ├── app/
│   │   ├── core/           # config.py · security.py · database.py
│   │   ├── models/         # schemas.py (Pydantic) · db_models.py (SQLAlchemy)
│   │   ├── routers/        # auth · carbon · predictions · tips
│   │   ├── services/       # carbon_calculator.py · ml_predictor.py
│   │   └── main.py         # FastAPI app, middleware, lifespan
│   ├── tests/
│   │   └── test_all.py     # 20+ deterministic unit tests
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html          # Single-file SPA (Chart.js, dark eco theme, ARIA compliant)
```

Full architecture diagram and database schema: [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## Quick Start

### Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# 4. Run the server
uvicorn app.main:app --reload --port 8000
```

API documentation: `http://localhost:8000/docs` (development mode only)

### Frontend

```bash
# Option A: open directly in browser
open frontend/index.html

# Option B: serve with Python
python -m http.server 5173 --directory frontend
```

### Run Tests

```bash
cd backend
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
```

---

## Security Highlights

- **JWT** with configurable expiry — HS256 signed, verified on every protected request
- **bcrypt** password hashing via passlib — plain text never stored or logged
- **Strict Pydantic validation** — negative values, invalid enums, and out-of-range inputs rejected at the schema layer before touching business logic
- **Rate limiting** via slowapi — 5 reg/min, 10 login/min, 30 calc/min per IP
- **Security headers** on every response — CSP, X-Frame-Options, HSTS, X-Content-Type-Options
- **CORS allowlist** from environment variables — wildcard `*` only in development
- **No secrets in code** — all credentials via `.env` (excluded from git)

---

## ML Model

- **Algorithm**: Polynomial Regression degree 2 via scikit-learn `Pipeline`
- **Why degree 2**: Captures the realistic "easy wins first, then plateau" reduction curve. A linear model assumes constant rate of improvement forever — physically implausible.
- **Regularisation**: Ridge (`alpha=1.0`) prevents overfitting on small historical datasets
- **Determinism**: Fixed `random_state=42` throughout — tests never flake
- **Real data path**: When a user has 3+ saved calculations, the model trains on real historical totals instead of simulated data

---

## Emission Factors (Sources)

| Category | Factor | Source |
|---|---|---|
| Petrol car | 0.192 kg CO₂e/km | EPA 2023 |
| EV (India grid) | 0.053 kg CO₂e/km | CEA 2023 |
| Electricity (India) | 0.716 kg CO₂e/kWh | CEA 2023 |
| Short-haul flight | 255 kg CO₂e/trip | ICAO |
| Long-haul flight | 1050 kg CO₂e/trip | ICAO |
| Vegan diet baseline | 1500 kg CO₂e/yr | Poore & Nemecek 2018 |

---

## Testing

20+ deterministic unit tests across 8 test classes:

| Class | Coverage |
|---|---|
| `TestTransportCalculation` | Zero input, petrol vs EV, flight emissions, types |
| `TestHomeCalculation` | Solar reduction, per-capita scaling, edge cases |
| `TestDietCalculation` | Vegan vs omnivore, waste multiplier, excess meat |
| `TestRatingAndPercentile` | All 5 tiers, monotonicity, bounds |
| `TestFullFootprint` | Total = sum of parts, valid rating, benchmark constants |
| `TestMLPrediction` | Determinism, output length, non-negative, trend literals |
| `TestInputValidation` | Negative values, invalid enums, out-of-range inputs |
| `TestSecurity` | bcrypt hashing, JWT roundtrip, tampered token rejection |

---

## License

MIT License — see `LICENSE` for details.  
*Built for Hack2Skill Challenge 3 · Carbon Footprint Awareness Platform*
