"""
AERO Intent Classification Service
Uses Groq Llama 3.3 70B (Primary) / Gemini (Fallback) / Rule-based (Last Resort)
Classifies raw emergency transcripts into structured intents BEFORE triage.
"""

import os
import json
import re
import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger("aero_intent")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


INTENT_PROMPT = """You are an expert emergency triage intent classifier for AERO — India's AI Emergency Response system.

Analyze the caller's message and extract structured intent information.

Caller message: "{text}"
Detected language: {language}

Return ONLY a valid JSON object (no markdown, no extra text):
{{
  "intent": "EMERGENCY_MEDICAL" | "EMERGENCY_ACCIDENT" | "EMERGENCY_FIRE" | "INFORMATION_REQUEST" | "NON_EMERGENCY",
  "sub_intent": "CARDIAC" | "RESPIRATORY" | "TRAUMA" | "NEUROLOGICAL" | "OBSTETRIC" | "BURN" | "POISONING" | "DROWNING" | "MENTAL_HEALTH" | "GENERAL",
  "confidence": 0.95,
  "urgency": "CRITICAL" | "HIGH" | "MODERATE" | "LOW",
  "requires_ambulance": true,
  "patient_count": 1,
  "key_symptoms": ["symptom1", "symptom2"],
  "extracted_location": null,
  "caller_distress_level": "EXTREME" | "HIGH" | "MODERATE" | "CALM"
}}

Rules:
- If caller mentions chest pain, heart attack, breathlessness → CARDIAC
- If caller mentions accident, collision, bleeding, fracture → TRAUMA  
- If caller mentions not breathing, choking, asthma attack → RESPIRATORY
- If caller mentions unconscious, seizure, paralysis, stroke → NEUROLOGICAL
- If caller mentions delivery, labor, pregnancy complication → OBSTETRIC
- For Gangetic belt dialects (Bhojpuri, Awadhi, Haryanvi), treat as Hindi
- If it sounds like a test or wrong number → NON_EMERGENCY"""


async def classify_intent(text: str, language: str = "English") -> Dict[str, Any]:
    """
    Classifies emergency intent using Groq Llama 3 8B (fastest),
    falling back to rule-based engine. (Gemini disabled per user request)
    """
    if GROQ_API_KEY:
        try:
            return await _groq_classify(text, language)
        except Exception as e:
            logger.warning(f"[Intent] Groq classification failed: {e}. Falling back to rule engine...")

    return _rule_based_classify(text)


async def _groq_classify(text: str, language: str) -> Dict[str, Any]:
    prompt = INTENT_PROMPT.format(text=text, language=language)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a JSON-only API. Respond strictly with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        result = json.loads(content)
        logger.info(f"[Intent] ✅ Groq: {result.get('intent')} / {result.get('sub_intent')}")
        return result


async def _gemini_classify(text: str, language: str) -> Dict[str, Any]:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.0-flash-lite",
        generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
    )
    prompt = INTENT_PROMPT.format(text=text, language=language)
    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    result = json.loads(raw)
    logger.info(f"[Intent] ✅ Gemini: {result.get('intent')} / {result.get('sub_intent')}")
    return result


def _rule_based_classify(text: str) -> Dict[str, Any]:
    """Fast keyword-based fallback classifier"""
    lower = text.lower()

    cardiac_kw = ["chest", "heart", "gunde", "seene", "dil", "attack", "noppi", "गुण्डे", "छाती", "दिल"]
    trauma_kw = ["accident", "blood", "fracture", "hit", "crash", "raktam", "rakht", "bleeding", "खून", "रक्त", "యాక్సిడెంట్"]
    resp_kw = ["breath", "saans", "opiri", "asthma", "suffocate", "choking", "ఊపిరి", "सांस"]
    neuro_kw = ["unconscious", "faint", "collapse", "seizure", "stroke", "behoshi", "spruha", "बेहोश"]
    obstetric_kw = ["delivery", "baby", "labor", "pregnant", "prasavam", "प्रसव", "प्रसूति"]

    intent = "EMERGENCY_MEDICAL"
    sub_intent = "GENERAL"
    urgency = "HIGH"

    if any(k in lower for k in cardiac_kw):
        sub_intent, urgency = "CARDIAC", "CRITICAL"
    elif any(k in lower for k in trauma_kw):
        intent, sub_intent, urgency = "EMERGENCY_ACCIDENT", "TRAUMA", "CRITICAL"
    elif any(k in lower for k in resp_kw):
        sub_intent, urgency = "RESPIRATORY", "CRITICAL"
    elif any(k in lower for k in neuro_kw):
        sub_intent, urgency = "NEUROLOGICAL", "CRITICAL"
    elif any(k in lower for k in obstetric_kw):
        sub_intent, urgency = "OBSTETRIC", "HIGH"

    return {
        "intent": intent,
        "sub_intent": sub_intent,
        "confidence": 0.75,
        "urgency": urgency,
        "requires_ambulance": urgency in ("CRITICAL", "HIGH"),
        "patient_count": 1,
        "key_symptoms": [sub_intent.lower().replace("_", " ")],
        "extracted_location": None,
        "caller_distress_level": "HIGH" if urgency == "CRITICAL" else "MODERATE"
    }
