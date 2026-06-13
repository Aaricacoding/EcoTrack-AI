import httpx
import json
import os
from app.models.schemas import InsightRequest, InsightResponse, ChatRequest, ChatResponse, CategoryBreakdown

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_MODEL = "llama-3.1-8b-instant"
_GLOBAL_AVG_KG = 4000.0
_INDIA_AVG_KG = 1800.0

def _get_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise ValueError("GROQ_API_KEY not set")
    return key

def _call_groq(prompt: str, system: str = "", max_tokens: int = 800) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": _MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    with httpx.Client(timeout=30.0) as client:
        res = client.post(
            _GROQ_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {_get_api_key()}"
            }
        )
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()

def _build_insight_prompt(req: InsightRequest) -> str:
    fp = req.footprint
    dominant = max(
        [("transport", fp.transport), ("home energy", fp.home_energy),
         ("diet", fp.diet), ("shopping", fp.shopping)],
        key=lambda x: x[1]
    )[0]
    name_part = f"for {req.user_name}" if req.user_name else "for this user"
    return f"""Analyse this carbon footprint and return ONLY a JSON object — no markdown, no extra text.

USER DATA:
- Transport: {fp.transport:.0f} kg CO2e/year
- Home Energy: {fp.home_energy:.0f} kg CO2e/year
- Diet: {fp.diet:.0f} kg CO2e/year
- Shopping: {fp.shopping:.0f} kg CO2e/year
- TOTAL: {fp.total:.0f} kg CO2e/year
- Global average: {_GLOBAL_AVG_KG:.0f} kg/year
- India average: {_INDIA_AVG_KG:.0f} kg/year
- IPCC 1.5C target: 2300 kg/year

Return EXACTLY this JSON:
{{
  "summary": "2-3 sentence overview {name_part} referencing their actual numbers vs benchmarks",
  "dominant_category": "{dominant}",
  "key_insight": "One non-obvious insight specific to this person's exact numbers",
  "action_plan": [
    "Step 1: concrete action with estimated CO2 saving",
    "Step 2: concrete action with estimated CO2 saving",
    "Step 3: concrete action with estimated CO2 saving"
  ],
  "motivational_close": "One encouraging sentence personalised {name_part}"
}}"""

async def generate_insights(req: InsightRequest) -> InsightResponse:
    fp = req.footprint
    dominant = max(
        [("transport", fp.transport), ("home energy", fp.home_energy),
         ("diet", fp.diet), ("shopping", fp.shopping)],
        key=lambda x: x[1]
    )[0]
    try:
        prompt = _build_insight_prompt(req)
        system = "You are an expert climate scientist and personal carbon coach. Always respond with valid JSON only."
        raw = _call_groq(prompt, system=system)
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw.strip())
        return InsightResponse(
            summary=parsed["summary"],
            dominant_category=parsed["dominant_category"],
            key_insight=parsed["key_insight"],
            action_plan=parsed["action_plan"],
            motivational_close=parsed["motivational_close"],
        )
    except Exception as e:
        return InsightResponse(
            summary=f"Your annual footprint of {fp.total:.0f} kg CO2e is {'above' if fp.total > _GLOBAL_AVG_KG else 'below'} the global average of {_GLOBAL_AVG_KG:.0f} kg. Your biggest driver is {dominant}.",
            dominant_category=dominant,
            key_insight=f"Reducing your {dominant} emissions by 30% would save {fp.total * 0.3:.0f} kg CO2e annually.",
            action_plan=[
                f"1. Focus on {dominant} — it drives the most impact.",
                "2. Track monthly changes to measure real progress.",
                "3. Start with the easiest win and build momentum.",
            ],
            motivational_close="Every kilogram reduced matters — small consistent changes compound over time.",
        )

async def chat_with_ecobot(req: ChatRequest) -> ChatResponse:
    fp = req.footprint_context
    system = "You are EcoBot, an expert carbon footprint coach. Keep responses under 150 words, warm and actionable. Never make up statistics."
    if fp:
        system += f"\nUser footprint: Transport {fp.transport:.0f}, Home {fp.home_energy:.0f}, Diet {fp.diet:.0f}, Shopping {fp.shopping:.0f}, Total {fp.total:.0f} kg CO2e/year (India avg: 1800, Global avg: 4000)"

    messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]
    payload = {
        "model": _MODEL,
        "messages": [{"role": "system", "content": system}] + messages,
        "max_tokens": 300,
        "temperature": 0.7
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(
                _GROQ_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {_get_api_key()}"
                }
            )
            res.raise_for_status()
            data = res.json()
            reply = data["choices"][0]["message"]["content"].strip()
            return ChatResponse(reply=reply)
    except Exception:
        return ChatResponse(reply="I'm having trouble connecting right now. Please try again in a moment.")
