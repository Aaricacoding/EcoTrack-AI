# Architecture — EcoTrack AI

## Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **ML**: scikit-learn (Ridge Regression + Isolation Forest)
- **AI**: Anthropic Claude API (insights + chatbot)
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Frontend**: Vanilla JS + Chart.js (single HTML file)

## API Endpoints

- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me
- POST /api/carbon/calculate
- POST /api/carbon/calculate/anonymous
- POST /api/predictions/forecast
- POST /api/tips/personalized
- POST /api/insights/analyze
- POST /api/insights/anomaly
- POST /api/insights/chat
- GET /health
