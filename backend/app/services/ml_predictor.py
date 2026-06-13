import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from datetime import datetime, timedelta, timezone
from typing import List
from app.models.schemas import CategoryBreakdown, PredictionResult, Tip

_RNG_SEED = 42

def _simulate_history(current_total: float, months_back: int = 6) -> np.ndarray:
    rng = np.random.default_rng(seed=(_RNG_SEED + int(round(current_total / 10))))
    history = []
    for i in range(months_back, 0, -1):
        noise = rng.uniform(-0.06, 0.06)
        trend = 1 + (i * 0.018)
        history.append(current_total * trend * (1 + noise))
    return np.array(history, dtype=np.float64)

def predict_future_footprint(breakdown: CategoryBreakdown, months_ahead: int = 6, historical_totals: list = None) -> PredictionResult:
    current_total = breakdown.total
    if historical_totals and len(historical_totals) >= 3:
        historical = np.array(historical_totals, dtype=np.float64)
    else:
        historical = _simulate_history(current_total)
    n = len(historical)
    X_train = np.arange(n).reshape(-1, 1)
    y_train = historical
    model = Pipeline([("poly", PolynomialFeatures(degree=2, include_bias=False)), ("reg", Ridge(alpha=1.0, random_state=_RNG_SEED))])
    model.fit(X_train, y_train)
    X_future = np.arange(n, n + months_ahead).reshape(-1, 1)
    raw_predictions = model.predict(X_future)
    predicted = np.clip(raw_predictions, 0.0, current_total * 3.0).tolist()
    now = datetime.now(timezone.utc)
    month_labels = [(now + timedelta(days=30 * i)).strftime("%b %Y") for i in range(1, months_ahead + 1)]
    first, last = predicted[0], predicted[-1]
    change_pct = (last - first) / max(abs(first), 1.0) * 100
    if change_pct < -5.0: trend = "improving"
    elif change_pct > 5.0: trend = "worsening"
    else: trend = "stable"
    max_category = max(breakdown.transport, breakdown.home_energy, breakdown.diet, breakdown.shopping)
    return PredictionResult(months=month_labels, predicted_kg=[round(p, 1) for p in predicted], trend=trend, reduction_potential_kg=round(max_category * 0.30, 2))

def generate_tips(breakdown: CategoryBreakdown) -> List[Tip]:
    tips = []
    p = 1
    if breakdown.transport > 2000:
        tips.append(Tip(category="transport", priority=p, title="Switch to an Electric Vehicle", description="EVs cut transport emissions by ~70%. India FAME-II subsidies reduce upfront cost significantly.", impact_kg_per_year=round(breakdown.transport * 0.65), difficulty="hard"))
        p += 1
    if breakdown.transport > 500:
        tips.append(Tip(category="transport", priority=p, title="Work from home 2 days per week", description="A 40% commute reduction directly cuts car and transit emissions.", impact_kg_per_year=round(breakdown.transport * 0.25), difficulty="medium"))
        p += 1
    if breakdown.transport > 300:
        tips.append(Tip(category="transport", priority=p, title="Replace one flight with train travel", description="Trains emit 90% less CO2 per km than domestic flights.", impact_kg_per_year=230, difficulty="easy"))
        p += 1
    if breakdown.home_energy > 800:
        tips.append(Tip(category="home_energy", priority=p, title="Install rooftop solar panels", description="A 2kW system covers 60-80% of Indian household electricity needs.", impact_kg_per_year=round(breakdown.home_energy * 0.60), difficulty="hard"))
        p += 1
    if breakdown.home_energy > 400:
        tips.append(Tip(category="home_energy", priority=p, title="Upgrade to 5-star BEE appliances", description="5-star rated appliances cut home energy use by 30-40%.", impact_kg_per_year=round(breakdown.home_energy * 0.30), difficulty="medium"))
        p += 1
    if breakdown.diet > 2000:
        tips.append(Tip(category="diet", priority=p, title="Try Meatless Mondays", description="One meat-free day per week saves 150-200 kg CO2e annually.", impact_kg_per_year=180, difficulty="easy"))
        p += 1
    if breakdown.diet > 2500:
        tips.append(Tip(category="diet", priority=p, title="Reduce food waste to low", description="Planning meals and composting scraps eliminates embedded food carbon.", impact_kg_per_year=round(breakdown.diet * 0.13), difficulty="easy"))
        p += 1
    if breakdown.shopping > 500:
        tips.append(Tip(category="shopping", priority=p, title="Buy second-hand clothing", description="10 second-hand items saves ~100kg CO2e and prevents textile waste.", impact_kg_per_year=round(breakdown.shopping * 0.20), difficulty="easy"))
        p += 1
    tips.sort(key=lambda t: t.impact_kg_per_year, reverse=True)
    return tips[:5]
