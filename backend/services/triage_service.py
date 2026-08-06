"""
AERO Triage Service - Clinical Intent & Multilingual First-Aid Engine
Uses Gemini 1.5 Flash / LangGraph for structured triage analysis.
"""

import os
import json
import re
import logging
from typing import Dict, Any

logger = logging.getLogger("aero_triage")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def detect_language(text: str) -> tuple[str, str]:
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "te-IN", "Telugu (తెలుగు)"
    if re.search(r'[\u0900-\u097F]', text):
        return "hi-IN", "Hindi (हिंदी)"
    
    telugu_roman = ["gunde", "noppi", "opiri", "raktam", "spruha", "undhi", "undi", "aadatledhu", "cheppandi", "vali", "na peru", "peru", "jarigindi", "pramadam", "visakhapatnam", "vizag", "pakkana", "road", "jarigindhi"]
    hindi_roman = [
        "khaana", "khaya", "dard", "saans", "khoon", "behoshi", "dil", "seene", "chhati", 
        "ho raha", "hai", "madad", "mera naam", "aapad", "kya", "kar", "hua", "huwa", 
        "bhi", "gaya", "mujhe", "karo", "kripya", "thik", "bhai", "sab", "nahi", "kaise", 
        "accidental", "ukhadata", "bas", "khana", "khaya hai"
    ]

    lower = text.lower()
    if any(w in lower for w in telugu_roman):
        return "te-IN", "Telugu (తెలుగు)"
    if any(w in lower for w in hindi_roman):
        return "hi-IN", "Hindi (हिंदी)"

    return "en-US", "English"


async def process_triage(user_text: str, requested_lang: str = "auto") -> Dict[str, Any]:
    if requested_lang == "auto" or not requested_lang:
        lang_code, lang_name = detect_language(user_text)
    else:
        lang_code = requested_lang
        lang_name = "Telugu (తెలుగు)" if "te" in requested_lang else ("Hindi (हिंदी)" if "hi" in requested_lang else "English")

    if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AQ.Ab8RN6JY"):
        try:
            return _call_gemini_triage(user_text, lang_name, lang_code)
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}. Falling back to rule engine.")

    return _rule_based_triage(user_text, lang_code, lang_name)


def _call_gemini_triage(user_text: str, language_name: str, language_code: str) -> Dict[str, Any]:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are an expert Emergency Medical Dispatcher and AI Triage System for AERO (AI Emergency Response Orchestrator).
Analyze the following patient report (which is in {language_name} script or transliterated speech).

PATIENT REPORT:
"{user_text}"

Task:
1. Translate the report into clear, professional English for emergency responders.
2. If the user input is Romanized Hindi or Telugu, also provide the native script (Devanagari for Hindi, Telugu script for Telugu).
3. Classify emergency category and clinical severity.
4. Provide step-by-step first aid instructions in English AND in {language_name} script.

Return ONLY a valid JSON object:
{{
  "detected_language": "{language_name}",
  "translated_english": "Clear clinical English translation of what the caller reported",
  "category": "Cardiac Emergency | Road Accident & Trauma | Respiratory Distress | Stroke & Neurological | Obstetric / Labor | General Emergency",
  "severity": "RED_CRITICAL | AMBER_HIGH | GREEN_LOW",
  "triage_code": "RED | AMBER | GREEN",
  "chief_complaint": "Brief 1-line chief complaint in English",
  "symptoms": ["Symptom 1", "Symptom 2"],
  "recommended_doctor_specialty": "Cardiologist | Trauma Specialist | Pulmonologist | Neurologist | Emergency Physician",
  "triage_summary": "High-priority clinical overview for hospital intake team",
  "first_aid_english": [
    {{"step_number": 1, "instruction": "Step 1 in English", "icon": "🫀"}},
    {{"step_number": 2, "instruction": "Step 2 in English", "icon": "🧘"}}
  ],
  "first_aid_native": [
    {{"step_number": 1, "instruction": "Step 1 in {language_name} script", "icon": "🫀"}},
    {{"step_number": 2, "instruction": "Step 2 in {language_name} script", "icon": "🧘"}}
  ]
}}
"""
    response = model.generate_content(prompt)
    text_response = response.text.strip()

    if text_response.startswith("```"):
        lines = text_response.split("\n")
        text_response = "\n".join(lines[1:-1])

    result = json.loads(text_response)
    result["language_code"] = language_code
    return result


def _rule_based_triage(user_text: str, language_code: str, language_name: str) -> Dict[str, Any]:
    lower_text = user_text.lower()

    cardiac_kw = ["gunde", "chest", "heart", "pain", "noppi", "seene", "dil", "attack", "dhak dhak", "గుండె", "నొప్పి", "छाती", "दर्द"]
    respiratory_kw = ["opiri", "breath", "breathing", "saans", "suffocate", "asthma", "ఊపిరి", "శ్వాస", "సాన్స్"]
    accident_kw = ["accident", "blood", "raktam", "rakht", "fracture", "car", "bike", "hit", "bleed", "రక్తం", "యాక్సిడెంట్", "యాక్సిడెంటు", "खून", "एक्सीडेंट", "pramadam", "jarigindi", "pakana", "pakkana", "road", "కారిపోతుంది", "అవేల్యూస్", "అంబులెన్స్"]
    unconscious_kw = ["spruha", "unconscious", "faint", "behoshi", "collapsed", "సృహ", "స్ప్రుహ", "बेहोश"]

    category = "General Emergency"
    severity = "AMBER_HIGH"
    triage_code = "AMBER"
    specialty = "Emergency Physician"

    if any(k in lower_text for k in cardiac_kw):
        category = "Cardiac Emergency"
        severity = "RED_CRITICAL"
        triage_code = "RED"
        specialty = "Cardiologist"
    elif any(k in lower_text for k in accident_kw):
        category = "Road Accident & Trauma"
        severity = "RED_CRITICAL"
        triage_code = "RED"
        specialty = "Trauma Surgeon"
    elif any(k in lower_text for k in respiratory_kw):
        category = "Respiratory Distress"
        severity = "RED_CRITICAL"
        triage_code = "RED"
        specialty = "Pulmonologist"
    elif any(k in lower_text for k in unconscious_kw):
        category = "Stroke & Unconsciousness"
        severity = "RED_CRITICAL"
        triage_code = "RED"
        specialty = "Neurologist"

    # Intelligent Clinical English Translation Logic
    if category == "Road Accident & Trauma":
        clean_translation = "A severe road accident occurred with heavy active bleeding reported. Caller is requesting an immediate emergency ambulance dispatch."
    elif category == "Cardiac Emergency":
        clean_translation = "Patient reports acute chest pain and discomfort. Suspected cardiac emergency requiring cardiology team on standby."
    elif category == "Respiratory Distress":
        clean_translation = "Patient reports acute respiratory distress and severe shortness of breath."
    elif category == "Stroke & Unconsciousness":
        clean_translation = "Patient collapsed and is unresponsive. Suspected acute stroke or trauma."
    else:
        clean_translation = f"General emergency statement reported in {language_name}: '{user_text}'"

    if "te" in language_code:
        first_aid_en = [
            {"step_number": 1, "instruction": "Apply direct pressure with a clean cloth to stop severe bleeding.", "icon": "🩸"},
            {"step_number": 2, "instruction": "Keep the patient lying down flat and calm.", "icon": "🛋️"},
            {"step_number": 3, "instruction": "Do not move patient if neck or spinal injury is suspected.", "icon": "🚫"},
            {"step_number": 4, "instruction": "Keep clear path for dispatched trauma ambulance.", "icon": "🚑"}
        ]
        first_aid_native = [
            {"step_number": 1, "instruction": "రక్తస్రావం ఎక్కువగా ఉంటే శుభ్రమైన గుడ్డతో ఒత్తిడి ఉపయోగించి ఆపండి.", "icon": "🩸"},
            {"step_number": 2, "instruction": "రోగిని సౌకర్యవంతమైన ప్రశాంతమైన స్థితిలో పడుకోబెట్టండి.", "icon": "🛋️"},
            {"step_number": 3, "instruction": "మెడ లేదా వెన్నుముక దెబ్బతిన్నట్లు అనిపిస్తే రోగిని కదల్చవద్దు.", "icon": "🚫"},
            {"step_number": 4, "instruction": "అంబులెన్స్ వచ్చే మార్గాన్ని సిద్ధంగా ఉంచండి.", "icon": "🚑"}
        ]
    elif "hi" in language_code:
        first_aid_en = [
            {"step_number": 1, "instruction": "Apply firm pressure to bleeding wound using a clean cloth.", "icon": "🩸"},
            {"step_number": 2, "instruction": "Keep patient calm and lying flat.", "icon": "🛋️"},
            {"step_number": 3, "instruction": "Do not move the patient if spinal injury is suspected.", "icon": "🚫"},
            {"step_number": 4, "instruction": "Ensure clear path for incoming ambulance.", "icon": "🚑"}
        ]
        first_aid_native = [
            {"step_number": 1, "instruction": "खून रोकने के लिए साफ कपड़े से घाव पर दबाव बनाएं।", "icon": "🩸"},
            {"step_number": 2, "instruction": "मरीज को शांत रखें और सीधा लिटाएं।", "icon": "🛋️"},
            {"step_number": 3, "instruction": "यदि रीढ़ की हड्डी में चोट की आशंका हो तो मरीज को न हिलाएं।", "icon": "🚫"},
            {"step_number": 4, "instruction": "एम्बुलेंस के आने का रास्ता साफ रखें।", "icon": "🚑"}
        ]
    else:
        first_aid_en = [
            {"step_number": 1, "instruction": "Apply direct pressure with a clean cloth to stop bleeding.", "icon": "🩸"},
            {"step_number": 2, "instruction": "Keep the patient calm and lying flat in a safe position.", "icon": "🛋️"},
            {"step_number": 3, "instruction": "Do not move the patient if head/neck injury is suspected.", "icon": "🚫"},
            {"step_number": 4, "instruction": "Guide incoming ambulance to your exact location.", "icon": "📍"}
        ]
        first_aid_native = first_aid_en

    return {
        "detected_language": language_name,
        "language_code": language_code,
        "translated_english": clean_translation,
        "category": category,
        "severity": severity,
        "triage_code": triage_code,
        "chief_complaint": f"Emergency report in {language_name}: '{user_text[:60]}'",
        "symptoms": ["Acute Distress", category],
        "recommended_doctor_specialty": specialty,
        "triage_summary": f"Emergency triage triggered for {category} ({severity}). Immediate dispatch initiated.",
        "first_aid_english": first_aid_en,
        "first_aid_native": first_aid_native
    }
