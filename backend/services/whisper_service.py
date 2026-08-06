"""
AERO Whisper Service — Upgraded Multilingual STT Engine
Supports ALL Indian languages via Groq Whisper Large v3:
Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, Bengali,
Gujarati, Punjabi, Odia, Assamese, Urdu, Bhojpuri/Awadhi (as hi),
Maithili (as hi), Sindhi, Kashmiri, and Indian English.
"""

import os
import io
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("aero_whisper")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ISO 639-1 codes accepted by Whisper for Indian languages
INDIAN_LANGUAGE_MAP = {
    # Full BCP-47 → Whisper ISO code
    "hi-IN": "hi",   # Hindi (covers Awadhi, Bhojpuri, Maithili, Haryanvi, Rajasthani)
    "te-IN": "te",   # Telugu
    "ta-IN": "ta",   # Tamil
    "kn-IN": "kn",   # Kannada
    "ml-IN": "ml",   # Malayalam
    "mr-IN": "mr",   # Marathi
    "bn-IN": "bn",   # Bengali
    "gu-IN": "gu",   # Gujarati
    "pa-IN": "pa",   # Punjabi
    "or-IN": "or",   # Odia
    "as-IN": "as",   # Assamese
    "ur-IN": "ur",   # Urdu
    "en-IN": "en",   # Indian English
    "en-US": "en",
    # Short codes
    "hi": "hi", "te": "te", "ta": "ta", "kn": "kn",
    "ml": "ml", "mr": "mr", "bn": "bn", "gu": "gu",
    "pa": "pa", "or": "or", "as": "as", "ur": "ur",
    "en": "en",
}


async def transcribe_audio_groq(
    audio_bytes: bytes,
    filename: str = "recording.webm",
    language: str = "auto",
    mime_type: str = "audio/webm"
) -> Dict[str, Any]:
    """
    Transcribes audio using Groq Whisper Large v3.
    - language="auto" → Whisper auto-detects (best for multilingual/code-switching)
    - language="hi-IN" → forces Hindi (catches all Gangetic dialects)
    - Returns: { success, text, detected_language, language_code, duration_seconds }
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set. Whisper unavailable.")
        return {"success": False, "text": "", "detected_language": "Unknown", "language_code": "en-US"}

    # Determine audio MIME type from filename extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    mime_map = {
        "webm": "audio/webm", "ogg": "audio/ogg", "mp4": "audio/mp4",
        "wav": "audio/wav", "mp3": "audio/mpeg", "m4a": "audio/mp4", "flac": "audio/flac"
    }
    audio_mime = mime_type or mime_map.get(ext, "audio/webm")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    form_data = {
        "model": "whisper-large-v3",
        "response_format": "verbose_json",  # Returns language + segments + duration
        "temperature": "0",                  # Deterministic
    }

    # Only pass language if explicitly requested — auto-detect is more powerful
    if language != "auto" and language in INDIAN_LANGUAGE_MAP:
        form_data["language"] = INDIAN_LANGUAGE_MAP[language]

    files = {"file": (filename, audio_bytes, audio_mime)}

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, headers=headers, data=form_data, files=files)

        if resp.status_code == 200:
            result = resp.json()
            text = result.get("text", "").strip()
            whisper_lang = result.get("language", "english").lower()
            duration = result.get("duration", 0)

            # Map Whisper language name → BCP-47 code
            lang_code = _whisper_lang_to_code(whisper_lang)
            lang_display = _code_to_display_name(lang_code)

            logger.info(f"[Whisper] ✅ '{text[:80]}' | lang={whisper_lang} | {duration:.1f}s")
            return {
                "success": True,
                "text": text,
                "detected_language": lang_display,
                "language_code": lang_code,
                "duration_seconds": duration,
            }
        else:
            logger.error(f"[Whisper] API error {resp.status_code}: {resp.text[:300]}")

    except Exception as e:
        logger.error(f"[Whisper] Exception: {e}")

    return {"success": False, "text": "", "detected_language": "Unknown", "language_code": "en-US"}


def _whisper_lang_to_code(whisper_lang: str) -> str:
    """Maps Whisper's language name output → BCP-47 code"""
    mapping = {
        "hindi": "hi-IN", "telugu": "te-IN", "tamil": "ta-IN",
        "kannada": "kn-IN", "malayalam": "ml-IN", "marathi": "mr-IN",
        "bengali": "bn-IN", "gujarati": "gu-IN", "punjabi": "pa-IN",
        "odia": "or-IN", "assamese": "as-IN", "urdu": "ur-IN",
        "english": "en-IN", "bhojpuri": "hi-IN",
    }
    return mapping.get(whisper_lang.lower(), "en-IN")


def _code_to_display_name(code: str) -> str:
    display = {
        "hi-IN": "Hindi (हिंदी)", "te-IN": "Telugu (తెలుగు)",
        "ta-IN": "Tamil (தமிழ்)", "kn-IN": "Kannada (ಕನ್ನಡ)",
        "ml-IN": "Malayalam (മലയാളം)", "mr-IN": "Marathi (मराठी)",
        "bn-IN": "Bengali (বাংলা)", "gu-IN": "Gujarati (ગુજરાતી)",
        "pa-IN": "Punjabi (ਪੰਜਾਬੀ)", "or-IN": "Odia (ଓଡ଼ିଆ)",
        "as-IN": "Assamese (অসমীয়া)", "ur-IN": "Urdu (اردو)",
        "en-IN": "English (India)",
    }
    return display.get(code, "English (India)")
