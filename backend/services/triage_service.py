"""
AERO Triage Service
Groq Llama 3.3 70B / Gemini powered multilingual clinical triage engine.
Supports: Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, Bengali,
Gujarati, Punjabi, Odia, Assamese, Urdu, and all Indian English variants.
"""

import os
import json
import re
import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger("aero_triage")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Language Detection ──────────────────────────────────────────────────────

SCRIPT_RANGES = [
    (r'[\u0C00-\u0C7F]', "te-IN", "Telugu (తెలుగు)"),
    (r'[\u0900-\u097F]', "hi-IN", "Hindi (हिंदी)"),
    (r'[\u0B80-\u0BFF]', "ta-IN", "Tamil (தமிழ்)"),
    (r'[\u0C80-\u0CFF]', "kn-IN", "Kannada (కನ್ನಡ)"),
    (r'[\u0D00-\u0D7F]', "ml-IN", "Malayalam (മലയാളം)"),
    (r'[\u0980-\u09FF]', "bn-IN", "Bengali (বাংলা)"),
    (r'[\u0A80-\u0AFF]', "gu-IN", "Gujarati (ગુજરાતી)"),
    (r'[\u0A00-\u0A7F]', "pa-IN", "Punjabi (ਪੰਜਾਬੀ)"),
    (r'[\u0B00-\u0B7F]', "or-IN", "Odia (ଓଡ଼ିଆ)"),
    (r'[\u0600-\u06FF]', "ur-IN", "Urdu (اردو)"),
]

HINDI_ROMAN_KW = [
    "dard", "saans", "khoon", "behoshi", "dil", "seene", "chhati",
    "ho raha", "madad", "mujhe", "karo", "kripya", "thik", "nahi",
    "accident", "laga", "gaya", "hua", "bhai", "aao", "jaldi", "bechaini",
    "ghabra", "bhaago", "bata", "dekho", "seedha"
]
TELUGU_ROMAN_KW = [
    "gunde", "noppi", "opiri", "raktam", "spruha", "undhi", "undi",
    "cheppandi", "vali", "jarigindi", "pramadam", "pakkana", "road",
    "vastunna", "padipoya", "ambulance", "doctor", "akka", "anna"
]


def detect_language(text: str) -> tuple:
    for pattern, code, name in SCRIPT_RANGES:
        if re.search(pattern, text):
            return code, name
    lower = text.lower()
    if any(w in lower for w in HINDI_ROMAN_KW):
        return "hi-IN", "Hindi (हिंदी)"
    if any(w in lower for w in TELUGU_ROMAN_KW):
        return "te-IN", "Telugu (తెలుగు)"
    return "en-IN", "English (India)"


# ── Triage Prompt ────────────────────────────────────────────────────────────

def _build_triage_prompt(user_text: str, lang_name: str, sub_intent: str = "GENERAL") -> str:
    return f"""You are an expert Emergency Medical Dispatcher for AERO — India's national AI emergency response system.

Patient report ({lang_name}):
"{user_text}"

Emergency sub-type identified: {sub_intent}

Task:
1. Translate the report to clear clinical English.
2. Classify emergency category and severity.
3. Provide 4-5 actionable first aid steps in BOTH English AND {lang_name} native script.
   - If the language is Telugu, write native steps in Telugu script (తెలుగు).
   - If the language is Hindi or Gangetic dialect, write native steps in Devanagari Hindi (हिंदी).
   - For all other languages, write native steps in their native script.

Return ONLY a valid JSON object matching this schema exactly:
{{
  "detected_language": "{lang_name}",
  "translated_english": "Clear clinical English summary of the report",
  "category": "Cardiac Emergency | Road Accident & Trauma | Respiratory Distress | Stroke & Neurological | Obstetric / Labor | Burns & Poisoning | General Emergency",
  "severity": "RED_CRITICAL | AMBER_HIGH | GREEN_LOW",
  "triage_code": "RED | AMBER | GREEN",
  "chief_complaint": "One-line chief complaint in English",
  "symptoms": ["Symptom 1", "Symptom 2", "Symptom 3"],
  "recommended_doctor_specialty": "Cardiologist | Trauma Surgeon | Pulmonologist | Neurologist | Obstetrician | Emergency Physician",
  "triage_summary": "Brief clinical summary for hospital intake team",
  "first_aid_english": [
    {{"step_number": 1, "instruction": "Action step in English", "icon": "🫀"}},
    {{"step_number": 2, "instruction": "Action step in English", "icon": "🧘"}}
  ],
  "first_aid_native": [
    {{"step_number": 1, "instruction": "Action step in {lang_name} script", "icon": "🫀"}},
    {{"step_number": 2, "instruction": "Action step in {lang_name} script", "icon": "🧘"}}
  ]
}}"""


# ── Main Triage Function ─────────────────────────────────────────────────────

async def process_triage(
    user_text: str,
    requested_lang: str = "auto",
    sub_intent: str = "GENERAL"
) -> Dict[str, Any]:
    if requested_lang in ("auto", None, ""):
        lang_code, lang_name = detect_language(user_text)
    else:
        lang_code = requested_lang
        lang_name = _code_to_name(requested_lang)

    # 1. Primary: Groq Llama 3.3 70B (Fast & High Quota)
    if GROQ_API_KEY:
        try:
            return await _call_groq_triage(user_text, lang_name, lang_code, sub_intent)
        except Exception as e:
            logger.warning(f"[Triage] Groq failed: {e}. Trying Gemini...")

    # 2. Fallback: Gemini
    if GEMINI_API_KEY:
        try:
            return await _call_gemini_triage(user_text, lang_name, lang_code, sub_intent)
        except Exception as e:
            logger.warning(f"[Triage] Gemini failed: {e}. Using rule engine...")

    # 3. Last Resort: Rule Engine
    return _rule_based_triage(user_text, lang_code, lang_name)


async def _call_groq_triage(
    user_text: str, lang_name: str, lang_code: str, sub_intent: str
) -> Dict[str, Any]:
    prompt = _build_triage_prompt(user_text, lang_name, sub_intent)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert medical dispatcher AI. Return strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        result = json.loads(content)
        result["language_code"] = lang_code
        logger.info(f"[Triage] ✅ Groq: {result.get('category')} | {result.get('severity')}")
        return result


async def _call_gemini_triage(
    user_text: str, lang_name: str, lang_code: str, sub_intent: str
) -> Dict[str, Any]:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.0-flash-lite",
        generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
    )
    prompt = _build_triage_prompt(user_text, lang_name, sub_intent)
    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    result = json.loads(raw)
    result["language_code"] = lang_code
    logger.info(f"[Triage] ✅ Gemini: {result.get('category')} | {result.get('severity')}")
    return result


def _code_to_name(code: str) -> str:
    m = {
        "hi-IN": "Hindi (हिंदी)", "te-IN": "Telugu (తెలుగు)",
        "ta-IN": "Tamil (தமிழ்)", "kn-IN": "Kannada (కನ್ನಡ)",
        "ml-IN": "Malayalam (മലയാളം)", "mr-IN": "Marathi (मराठी)",
        "bn-IN": "Bengali (বাংলা)", "gu-IN": "Gujarati (ગુજરાતી)",
        "pa-IN": "Punjabi (ਪੰਜਾਬੀ)", "or-IN": "Odia (ଓଡ଼ိଆ)",
        "ur-IN": "Urdu (اردو)", "en-IN": "English (India)",
    }
    return m.get(code, "English (India)")


# ── Rule-Based Fallback ──────────────────────────────────────────────────────

def _rule_based_triage(user_text: str, lang_code: str, lang_name: str) -> Dict[str, Any]:
    lower = user_text.lower()

    rules = [
        (["gunde", "chest", "heart", "seene", "dil", "attack", "noppi", "छाती", "दर्द", "গুণ্ডె"],
         "Cardiac Emergency", "RED_CRITICAL", "RED", "Cardiologist",
         "Acute chest pain with suspected cardiac episode."),
        (["accident", "blood", "raktam", "rakht", "fracture", "crash", "bleed", "రక్తం", "खून", "रक्त"],
         "Road Accident & Trauma", "RED_CRITICAL", "RED", "Trauma Surgeon",
         "Severe traumatic injury with active hemorrhage reported."),
        (["breath", "saans", "opiri", "asthma", "suffocate", "choke", "ఊపిరి", "सांस"],
         "Respiratory Distress", "RED_CRITICAL", "RED", "Pulmonologist",
         "Severe respiratory compromise with inability to breathe."),
        (["unconscious", "faint", "collapse", "seizure", "stroke", "behoshi", "spruha", "बेहोश"],
         "Stroke & Neurological", "RED_CRITICAL", "RED", "Neurologist",
         "Sudden loss of consciousness or neurological event."),
        (["delivery", "baby", "labor", "pregnant", "prasavam", "प्रसव"],
         "Obstetric / Labor", "AMBER_HIGH", "AMBER", "Obstetrician",
         "Active labor or obstetric complication reported."),
        (["burn", "fire", "jala", "jalana", "కాలిపోయింది", "जला"],
         "Burns & Poisoning", "AMBER_HIGH", "AMBER", "Emergency Physician",
         "Burn injury or toxic exposure reported."),
    ]

    category = "General Emergency"
    severity = "AMBER_HIGH"
    triage_code = "AMBER"
    specialty = "Emergency Physician"
    summary = f"General emergency reported in {lang_name}."

    for kws, cat, sev, code, spec, summ in rules:
        if any(k in lower for k in kws):
            category, severity, triage_code, specialty, summary = cat, sev, code, spec, summ
            break

    first_aid_map = {
        "Cardiac Emergency": (
            [{"step_number": 1, "instruction": "Have patient sit or lie still, loosen tight clothing.", "icon": "👕"},
             {"step_number": 2, "instruction": "If patient stops breathing, begin CPR immediately.", "icon": "🫀"},
             {"step_number": 3, "instruction": "Do NOT give food or water.", "icon": "🚫"},
             {"step_number": 4, "instruction": "Keep patient calm and wait for ambulance.", "icon": "🚑"}],
            {"hi-IN": [{"step_number": 1, "instruction": "मरीज को बैठाएं या लिटाएं, कपड़े ढीले करें।", "icon": "👕"},
                       {"step_number": 2, "instruction": "सांस रुके तो CPR शुरू करें।", "icon": "🫀"},
                       {"step_number": 3, "instruction": "कुछ खाने-पीने को न दें।", "icon": "🚫"},
                       {"step_number": 4, "instruction": "एम्बुलेंस आने तक शांत रखें।", "icon": "🚑"}],
             "te-IN": [{"step_number": 1, "instruction": "రోగిని కూర్చోబెట్టండి, బట్టలు వదులు చేయండి.", "icon": "👕"},
                       {"step_number": 2, "instruction": "శ్వాస ఆగితే CPR ప్రారంభించండి.", "icon": "🫀"},
                       {"step_number": 3, "instruction": "తినడానికి లేదా త్రాగడానికి ఇవ్వకండి.", "icon": "🚫"},
                       {"step_number": 4, "instruction": "అంబులెన్స్ కోసం వేచి ఉండండి.", "icon": "🚑"}]}
        ),
        "Road Accident & Trauma": (
            [{"step_number": 1, "instruction": "Apply firm pressure with clean cloth to bleeding wounds.", "icon": "🩸"},
             {"step_number": 2, "instruction": "Do NOT move patient if neck or spine injury suspected.", "icon": "🚫"},
             {"step_number": 3, "instruction": "Keep patient warm and flat.", "icon": "🛋️"},
             {"step_number": 4, "instruction": "Clear path for incoming ambulance.", "icon": "🚑"}],
            {"hi-IN": [{"step_number": 1, "instruction": "घाव पर साफ कपड़े से दबाव बनाएं।", "icon": "🩸"},
                       {"step_number": 2, "instruction": "रीढ़ की हड्डी में चोट हो तो मत हिलाएं।", "icon": "🚫"},
                       {"step_number": 3, "instruction": "मरीज को गर्म और लेटे हुए रखें।", "icon": "🛋️"},
                       {"step_number": 4, "instruction": "एम्बुलेंस का रास्ता साफ रखें।", "icon": "🚑"}],
             "te-IN": [{"step_number": 1, "instruction": "రక్తస్రావానికి శుభ్రమైన గుడ్డతో ఒత్తిడి వేయండి.", "icon": "🩸"},
                       {"step_number": 2, "instruction": "మెడ దెబ్బతింటే కదల్చవద్దు.", "icon": "🚫"},
                       {"step_number": 3, "instruction": "రోగిని వెచ్చగా ఉంచి పడుకోబెట్టండి.", "icon": "🛋️"},
                       {"step_number": 4, "instruction": "అంబులెన్స్ మార్గం ఖాళీగా ఉంచండి.", "icon": "🚑"}]}
        ),
    }

    en_steps, native_map = first_aid_map.get(category, (
        [{"step_number": 1, "instruction": "Stay calm and keep the patient comfortable.", "icon": "🧘"},
         {"step_number": 2, "instruction": "Call 108 (ambulance) immediately.", "icon": "📞"},
         {"step_number": 3, "instruction": "Do not leave the patient alone.", "icon": "👁️"},
         {"step_number": 4, "instruction": "Monitor breathing until help arrives.", "icon": "🫁"}],
        {}
    ))

    native_steps = native_map.get(lang_code, en_steps)

    return {
        "detected_language": lang_name,
        "language_code": lang_code,
        "translated_english": summary,
        "category": category,
        "severity": severity,
        "triage_code": triage_code,
        "chief_complaint": summary,
        "symptoms": ["Acute distress", category],
        "recommended_doctor_specialty": specialty,
        "triage_summary": f"{category} ({severity}) — immediate response required.",
        "first_aid_english": en_steps,
        "first_aid_native": native_steps,
    }
