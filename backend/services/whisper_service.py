"""
AERO Whisper Service - SOTA Multilingual Audio Transcription using Groq Whisper Large v3
Handles native Telugu, Hindi, Indian English, and transliterated speech audio streams with high precision.
"""

import os
import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger("aero_whisper")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

async def transcribe_audio_groq(audio_bytes: bytes, filename: str = "recording.webm", language: str = "auto") -> Dict[str, Any]:
    """
    Transcribes audio using Groq Whisper Large v3 API.
    Supports Telugu, Hindi, English, and Hinglish/Telugish accents.
    """
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("your-groq"):
        logger.warning("GROQ_API_KEY not configured. Falling back to Gemini audio processing.")
        return {"success": False, "text": ""}

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": (filename, audio_bytes, "audio/webm")
    }
    
    data = {
        "model": "whisper-large-v3",
        "response_format": "json"
    }

    if language in ["te-IN", "te"]:
        data["language"] = "te"
    elif language in ["hi-IN", "hi"]:
        data["language"] = "hi"
    elif language in ["en-IN", "en-US", "en"]:
        data["language"] = "en"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            if response.status_code == 200:
                result = response.json()
                transcribed_text = result.get("text", "").strip()
                logger.info(f"Groq Whisper transcription success: {transcribed_text}")
                return {"success": True, "text": transcribed_text}
            else:
                logger.error(f"Groq Whisper API returned error {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Groq Whisper transcription exception: {e}")

    return {"success": False, "text": ""}
