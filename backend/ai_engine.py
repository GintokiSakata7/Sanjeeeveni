"""
AERO AI Engine Orchestrator — Upgraded
Pipeline: Whisper STT → Intent Classification → Triage → Response
"""

import logging
from typing import Dict, Any

from services.whisper_service import transcribe_audio_groq
from services.intent_service import classify_intent
from services.triage_service import process_triage, detect_language

logger = logging.getLogger("aero_ai_engine")


async def analyze_emergency(user_text: str, requested_lang: str = "auto") -> Dict[str, Any]:
    """
    Text-based emergency pipeline:
    1. Auto-detect language
    2. Classify intent (Gemini 1.5 Flash)
    3. Run triage with intent context
    """
    # 1. Detect language
    if requested_lang in ("auto", None, ""):
        lang_code, lang_name = detect_language(user_text)
    else:
        lang_code = requested_lang
        lang_name = requested_lang

    # 2. Intent classification
    intent_result = await classify_intent(user_text, lang_name)
    sub_intent = intent_result.get("sub_intent", "GENERAL")

    # 3. Triage with sub_intent context
    triage_result = await process_triage(user_text, lang_code, sub_intent)

    # 4. Merge intent data into triage response
    triage_result["intent"] = intent_result.get("intent", "EMERGENCY_MEDICAL")
    triage_result["intent_confidence"] = intent_result.get("confidence", 0.8)
    triage_result["requires_ambulance"] = intent_result.get("requires_ambulance", True)
    triage_result["caller_distress_level"] = intent_result.get("caller_distress_level", "HIGH")
    triage_result["extracted_location"] = intent_result.get("extracted_location")
    triage_result["national_helplines"] = _get_national_helplines()

    return triage_result


async def analyze_audio_emergency(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    requested_lang: str = "auto"
) -> Dict[str, Any]:
    """
    Full audio pipeline:
    1. Whisper Large v3 STT (auto-detect language)
    2. Intent classification
    3. Triage with sub_intent context
    """
    # 1. Whisper STT
    whisper_res = await transcribe_audio_groq(
        audio_bytes,
        filename="recording.webm",
        language=requested_lang,
        mime_type=mime_type
    )

    if whisper_res["success"] and whisper_res["text"]:
        transcribed_text = whisper_res["text"]
        detected_lang_code = whisper_res.get("language_code", "en-IN")
        detected_lang_display = whisper_res.get("detected_language", "English (India)")

        logger.info(f"[Engine] Whisper: '{transcribed_text[:80]}' [{detected_lang_display}]")

        # 2. Intent classification
        intent_result = await classify_intent(transcribed_text, detected_lang_display)
        sub_intent = intent_result.get("sub_intent", "GENERAL")

        # 3. Triage
        triage_result = await process_triage(transcribed_text, detected_lang_code, sub_intent)

        # 4. Merge
        triage_result["transcribed_text"] = transcribed_text
        triage_result["whisper_detected_language"] = detected_lang_display
        triage_result["intent"] = intent_result.get("intent", "EMERGENCY_MEDICAL")
        triage_result["intent_confidence"] = intent_result.get("confidence", 0.8)
        triage_result["requires_ambulance"] = intent_result.get("requires_ambulance", True)
        triage_result["caller_distress_level"] = intent_result.get("caller_distress_level", "HIGH")
        triage_result["extracted_location"] = intent_result.get("extracted_location")
        triage_result["national_helplines"] = _get_national_helplines()

        return triage_result

    # Gemini direct audio fallback
    logger.info("[Engine] Whisper failed, using Gemini audio fallback...")
    return await _gemini_audio_fallback(audio_bytes, mime_type, requested_lang)


async def _gemini_audio_fallback(audio_bytes: bytes, mime_type: str, requested_lang: str) -> Dict[str, Any]:
    """Direct Gemini multimodal audio analysis as last resort"""
    import os
    import json
    import re

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        return await process_triage("Emergency call received.", requested_lang, "GENERAL")

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-2.0-flash-lite",
            generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
        )
        prompt = """You are an emergency dispatcher AI. Analyze this audio recording from an Indian emergency caller.
Transcribe and triage it. Return JSON with keys:
transcribed_text, detected_language, language_code, translated_english, category, severity,
triage_code, chief_complaint, symptoms, recommended_doctor_specialty, triage_summary,
first_aid_english (array of {step_number, instruction, icon}),
first_aid_native (array of {step_number, instruction, icon})"""

        response = model.generate_content([{"mime_type": mime_type, "data": audio_bytes}, prompt])
        raw = re.sub(r"^```[a-z]*\n?", "", response.text.strip())
        raw = re.sub(r"\n?```$", "", raw)
        result = json.loads(raw)
        result["national_helplines"] = _get_national_helplines()
        return result
    except Exception as e:
        logger.error(f"[Engine] Gemini audio fallback failed: {e}")
        return await process_triage("Emergency call received.", requested_lang, "GENERAL")


def _get_national_helplines() -> list:
    """India national emergency helplines — shown as placeholder dispatch"""
    return [
        {"name": "National Ambulance (108)", "number": "108", "icon": "🚑", "available": "24/7"},
        {"name": "Police Emergency (112)", "number": "112", "icon": "🚔", "available": "24/7"},
        {"name": "Fire & Rescue (101)", "number": "101", "icon": "🔥", "available": "24/7"},
        {"name": "Women Helpline (1091)", "number": "1091", "icon": "👩", "available": "24/7"},
        {"name": "Disaster Management (1078)", "number": "1078", "icon": "⚠️", "available": "24/7"},
    ]
