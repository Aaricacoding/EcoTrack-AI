# backend/app/routers/insights.py
# Three AI-powered endpoints:
#   POST /api/insights/analyze  — Claude generates personalised narrative analysis
#   POST /api/insights/anomaly  — Isolation Forest flags unusual emission spikes
#   POST /api/chat/message      — Multi-turn EcoBot chatbot powered by Claude

from fastapi import APIRouter, status                   # FastAPI core
from app.models.schemas import (                        # Request/response models
    InsightRequest, InsightResponse,
    AnomalyRequest, AnomalyResult,
    ChatRequest, ChatResponse,
)
from app.services.ai_insights import generate_insights, chat_with_ecobot  # Claude API calls
from app.services.anomaly_detector import detect_anomaly                   # Isolation Forest

router = APIRouter()   # Mounted at /api/insights in main.py


# ── POST /api/insights/analyze ────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=InsightResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI-powered personalised carbon footprint analysis",
    description=(
        "Sends the user's footprint breakdown to Claude which returns a structured "
        "natural-language analysis: summary, dominant category, key non-obvious insight, "
        "3-step action plan, and a motivational closing statement. "
        "Falls back gracefully if the Anthropic API is unavailable."
    ),
)
async def analyze(req: InsightRequest) -> InsightResponse:
    """
    Claude reads the exact kg CO₂e numbers and generates a personalised narrative.
    Unlike hardcoded tips, this adapts to every possible combination of inputs.
    Async because it awaits the Anthropic API HTTP call.
    """
    return await generate_insights(req)   # Delegate to AI service layer


# ── POST /api/insights/anomaly ────────────────────────────────────────────────

@router.post(
    "/anomaly",
    response_model=AnomalyResult,
    status_code=status.HTTP_200_OK,
    summary="Detect anomalous emission spikes using Isolation Forest ML",
    description=(
        "Trains an Isolation Forest on the user's personal emission history "
        "and evaluates whether the current reading is a statistical outlier. "
        "Returns per-category z-scores and a human-readable explanation. "
        "Requires at least 3 historical records."
    ),
)
def anomaly(req: AnomalyRequest) -> AnomalyResult:
    """
    Synchronous — Isolation Forest runs in-process, no external API call needed.
    Uses the user's own history as the baseline, not a global threshold.
    """
    return detect_anomaly(req)   # Pure scikit-learn, deterministic with fixed seed


# ── POST /api/chat/message ────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with EcoBot — AI carbon coach powered by Claude",
    description=(
        "Multi-turn conversational endpoint. Send the full conversation history "
        "and optionally the user's footprint breakdown for context-aware answers. "
        "EcoBot answers questions about emissions, reduction strategies, and the "
        "user's specific data. Falls back gracefully if API is unavailable."
    ),
)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Claude maintains conversation context via the messages history array.
    The user's footprint is injected into the system prompt so EcoBot can
    give personalised answers like 'your transport is 3× your diet emissions'.
    Async because it awaits the Anthropic API HTTP call.
    """
    return await chat_with_ecobot(req)   # Delegate to AI service layer
