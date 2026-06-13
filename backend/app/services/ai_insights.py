# backend/app/services/ai_insights.py
# AI-powered carbon analysis using the Anthropic Claude API.
# Generates truly personalised natural-language insights — not hardcoded tip strings.
# Each user gets a unique analysis based on their exact breakdown numbers.

import httpx                                            # Async HTTP client for API calls
import json                                             # Parse Claude's JSON response
import os                                               # Read ANTHROPIC_API_KEY from env
from app.models.schemas import (
    InsightRequest, InsightResponse,
    ChatRequest, ChatResponse, ChatMessage,
    CategoryBreakdown,
)

# Anthropic API endpoint — using the messages API
_API_URL = "https://api.anthropic.com/v1/messages"
_MODEL   = "claude-sonnet-4-20250514"                  # Best balance of quality and speed
_HEADERS = {
    "content-type": "application/json",
    "anthropic-version": "2023-06-01",                 # Required version header
    # x-api-key is added at call time from environment — never hardcoded here
}

# Global averages for context injection into prompts
_GLOBAL_AVG_KG = 4000.0
_INDIA_AVG_KG  = 1800.0


def _get_api_key() -> str:
    """
    Read API key from environment variable at call time — not at import time.
    This means the server starts fine even without the key; only fails on actual AI calls.
    """
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return key


def _build_insight_prompt(req: InsightRequest) -> str:
    """
    Build a structured prompt that gives Claude all the numerical context it needs
    to produce a specific, data-grounded analysis rather than generic advice.
    """
    fp = req.footprint
    name_part = f"for {req.user_name}" if req.user_name else "for this user"
    dominant = max(
        [("transport", fp.transport), ("home energy", fp.home_energy),
         ("diet", fp.diet), ("shopping", fp.shopping)],
        key=lambda x: x[1]
    )[0]

    return f"""You are an expert climate scientist and personal carbon coach.
Analyse this carbon footprint data and return ONLY a JSON object — no markdown, no explanation outside the JSON.

USER FOOTPRINT DATA:
- Transport:    {fp.transport:.0f} kg CO₂e/year
- Home Energy:  {fp.home_energy:.0f} kg CO₂e/year
- Diet:         {fp.diet:.0f} kg CO₂e/year
- Shopping:     {fp.shopping:.0f} kg CO₂e/year
- TOTAL:        {fp.total:.0f} kg CO₂e/year
- Country:      {req.country}
- Dominant category: {dominant}

BENCHMARKS:
- Global average: {_GLOBAL_AVG_KG:.0f} kg/year
- India average:  {_INDIA_AVG_KG:.0f} kg/year
- IPCC 1.5°C target: 2300 kg/year by 2030

Return EXACTLY this JSON structure (all fields required):
{{
  "summary": "2-3 sentence plain-English overview of the footprint situation {name_part}, referencing their actual numbers vs benchmarks",
  "dominant_category": "{dominant}",
  "key_insight": "One non-obvious insight that a generic tip engine would miss — specific to this person's exact numbers",
  "action_plan": [
    "Step 1: concrete action with estimated kg CO₂e saving",
    "Step 2: concrete action with estimated kg CO₂e saving",
    "Step 3: concrete action with estimated kg CO₂e saving"
  ],
  "motivational_close": "One encouraging sentence that acknowledges the challenge and motivates action, personalised {name_part}"
}}"""


def _build_system_prompt(footprint_context: CategoryBreakdown | None) -> str:
    """
    System prompt for the carbon chatbot.
    Injects the user's actual footprint data so Claude can answer personal questions.
    """
    base = (
        "You are EcoBot, an expert carbon footprint coach built into EcoTrack AI. "
        "You are knowledgeable about climate science, Indian energy systems, sustainable living, "
        "and behaviour change. Keep responses concise (under 150 words), warm, and actionable. "
        "Never make up statistics — if uncertain, say so. "
        "Always relate advice back to the user's actual data when available."
    )

    if footprint_context:
        fp = footprint_context
        base += (
            f"\n\nCURRENT USER'S FOOTPRINT:"
            f"\n- Transport: {fp.transport:.0f} kg CO₂e/year"
            f"\n- Home Energy: {fp.home_energy:.0f} kg CO₂e/year"
            f"\n- Diet: {fp.diet:.0f} kg CO₂e/year"
            f"\n- Shopping: {fp.shopping:.0f} kg CO₂e/year"
            f"\n- Total: {fp.total:.0f} kg CO₂e/year (India avg: 1800, Global avg: 4000)"
        )

    return base


async def generate_insights(req: InsightRequest) -> InsightResponse:
    """
    Call Claude API to generate a personalised carbon analysis.
    Prompts Claude to return structured JSON so we can parse it into InsightResponse fields.
    Falls back gracefully if the API is unavailable (demo mode).
    """
    prompt = _build_insight_prompt(req)

    payload = {
        "model": _MODEL,
        "max_tokens": 800,                             # Enough for the JSON response
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:   # 30s timeout — AI calls can be slow
            response = await client.post(
                _API_URL,
                headers={**_HEADERS, "x-api-key": _get_api_key()},
                json=payload,
            )
            response.raise_for_status()              # Raises on 4xx/5xx
            data = response.json()

        # Extract text content from Claude's response
        raw_text = data["content"][0]["text"].strip()

        # Strip markdown code fences if Claude wraps in ```json ... ```
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        parsed = json.loads(raw_text)                 # Parse structured JSON from Claude

        return InsightResponse(
            summary=parsed["summary"],
            dominant_category=parsed["dominant_category"],
            key_insight=parsed["key_insight"],
            action_plan=parsed["action_plan"],
            motivational_close=parsed["motivational_close"],
        )

    except Exception as e:
        # Graceful fallback — never crash the endpoint if Claude is unreachable
        fp = req.footprint
        dominant = max(
            [("transport", fp.transport), ("home energy", fp.home_energy),
             ("diet", fp.diet), ("shopping", fp.shopping)],
            key=lambda x: x[1]
        )[0]

        return InsightResponse(
            summary=(
                f"Your annual footprint of {fp.total:.0f} kg CO₂e is "
                f"{'above' if fp.total > _GLOBAL_AVG_KG else 'below'} the global average of "
                f"{_GLOBAL_AVG_KG:.0f} kg. Your biggest driver is {dominant}."
            ),
            dominant_category=dominant,
            key_insight=f"Reducing your {dominant} emissions by 30% would save {fp.total * 0.3:.0f} kg CO₂e annually.",
            action_plan=[
                f"1. Focus on {dominant} — it's {max(fp.transport, fp.home_energy, fp.diet, fp.shopping) / fp.total * 100:.0f}% of your total.",
                "2. Track monthly changes to measure real progress.",
                "3. Start with the easiest win and build momentum.",
            ],
            motivational_close="Every tonne reduced matters — small consistent changes compound over time.",
        )


async def chat_with_ecobot(req: ChatRequest) -> ChatResponse:
    """
    Multi-turn conversational chatbot about carbon footprint.
    Maintains conversation history so the user can ask follow-up questions naturally.
    Injects the user's footprint data into the system prompt for context-aware answers.
    """
    # Convert our ChatMessage models to Anthropic API format
    api_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in req.messages
    ]

    payload = {
        "model": _MODEL,
        "max_tokens": 400,                             # Short responses — chatbot style
        "system": _build_system_prompt(req.footprint_context),
        "messages": api_messages,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                _API_URL,
                headers={**_HEADERS, "x-api-key": _get_api_key()},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        reply_text = data["content"][0]["text"].strip()
        return ChatResponse(reply=reply_text)

    except Exception:
        # Graceful fallback so frontend doesn't break if API key missing
        return ChatResponse(
            reply="I'm having trouble connecting right now. Please try again in a moment.",
        )
