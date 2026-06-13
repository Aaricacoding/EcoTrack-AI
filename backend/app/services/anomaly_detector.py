# backend/app/services/anomaly_detector.py
# Real ML anomaly detection using scikit-learn's Isolation Forest.
# Detects statistically unusual emission spikes in a user's personal history.
# This is genuine unsupervised ML — not regression, not hardcoded rules.

import numpy as np                                              # Array operations
from sklearn.ensemble import IsolationForest                   # Unsupervised anomaly detection
from sklearn.preprocessing import StandardScaler               # Normalise features before scoring
from app.models.schemas import AnomalyRequest, AnomalyResult  # Input/output models

# Fixed random state — ensures Isolation Forest produces identical trees every run
_RANDOM_STATE = 42

# Categories we analyse — order matters for array indexing
_CATEGORIES = ["transport", "home_energy", "diet", "shopping"]


def _breakdown_to_array(bd) -> list[float]:
    """Convert a CategoryBreakdown object to a flat list in consistent category order."""
    return [bd.transport, bd.home_energy, bd.diet, bd.shopping]


def detect_anomaly(req: AnomalyRequest) -> AnomalyResult:
    """
    Run Isolation Forest on the user's historical emission records to determine
    whether the current reading is a statistical anomaly.

    How Isolation Forest works:
    - Builds random decision trees that try to isolate each data point.
    - Anomalies are isolated faster (fewer splits needed) because they're far from
      the cluster of normal data — they get low anomaly scores.
    - contamination=0.15 means we expect ~15% of historical points might be outliers,
      which is realistic for monthly carbon data with lifestyle changes.

    Why this is better than a simple threshold check:
    - It learns the user's personal baseline — someone who normally drives a lot
      won't be flagged just for having a high transport score.
    - It detects multivariate anomalies — unusual combinations across categories,
      not just single-category spikes.
    """
    # Build feature matrix from historical records — shape (n_months, 4)
    history_arrays = [_breakdown_to_array(h) for h in req.history]
    X_history = np.array(history_arrays, dtype=np.float64)

    # Current data point to evaluate — shape (1, 4)
    X_current = np.array([_breakdown_to_array(req.current)], dtype=np.float64)

    # Normalise features — prevents high-magnitude categories (diet ~2500) from
    # dominating low-magnitude ones (shopping ~400) in the anomaly score
    scaler = StandardScaler()
    X_history_scaled = scaler.fit_transform(X_history)     # Fit on history, not current
    X_current_scaled = scaler.transform(X_current)          # Transform current with same scaler

    # Train Isolation Forest on the user's personal history
    clf = IsolationForest(
        n_estimators=100,          # 100 trees — enough for stability on small datasets
        contamination=0.15,        # Expect ~15% anomalies in history (lifestyle change events)
        random_state=_RANDOM_STATE,
        max_samples="auto",        # Auto-select sample size based on dataset size
    )
    clf.fit(X_history_scaled)

    # Score the current point: -1 = anomaly, 1 = normal
    prediction = clf.predict(X_current_scaled)[0]
    # Raw score — more negative = more anomalous
    raw_score = float(clf.score_samples(X_current_scaled)[0])

    is_anomaly = prediction == -1   # Isolation Forest convention: -1 means outlier

    # ── Per-category z-scores ──────────────────────────────────────────────────
    # Z-score tells us how many standard deviations above/below the user's mean
    # each category is — pinpoints WHICH category caused the anomaly
    history_mean = X_history.mean(axis=0)    # Mean per category across all historical months
    history_std  = X_history.std(axis=0)     # Std per category

    current_vals = _breakdown_to_array(req.current)
    z_scores: dict[str, float] = {}
    flagged: list[str] = []

    for i, cat in enumerate(_CATEGORIES):
        std = history_std[i] if history_std[i] > 0 else 1.0   # Avoid division by zero
        z = (current_vals[i] - history_mean[i]) / std
        z_scores[cat] = round(float(z), 2)

        # Flag category if z-score > 2.0 — more than 2 standard deviations above personal mean
        if z > 2.0:
            flagged.append(cat)

    # ── Human-readable explanation ─────────────────────────────────────────────
    if not is_anomaly:
        explanation = "Your emission levels are consistent with your recent history."
    elif flagged:
        # Describe which specific categories spiked
        cat_descriptions = {
            "transport": "transport (driving/flights)",
            "home_energy": "home energy usage",
            "diet": "diet choices",
            "shopping": "shopping activity",
        }
        flagged_readable = " and ".join(cat_descriptions.get(c, c) for c in flagged)
        z_max = max(z_scores[c] for c in flagged)
        explanation = (
            f"Unusual spike detected in {flagged_readable}. "
            f"Your highest flagged category is {round(z_max, 1)}× your typical standard deviation above your personal average. "
            f"Check for one-off events like a long trip, unusually high electricity bill, or major purchase."
        )
    else:
        # Isolation Forest flagged it but no single category z-score > 2 — multivariate anomaly
        explanation = (
            "Your overall emission pattern this period is unusual compared to your history, "
            "though no single category stands out dramatically. "
            "This may reflect a combination of small increases across multiple areas."
        )

    return AnomalyResult(
        is_anomaly=is_anomaly,
        anomaly_score=raw_score,
        z_scores=z_scores,
        flagged_categories=flagged,
        explanation=explanation,
    )
