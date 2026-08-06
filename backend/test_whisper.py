#!/usr/bin/env python
import base64, json, pathlib, requests

# -------------------------------------------------
# 1️⃣  Make sure the FastAPI server is up:
#     uvicorn main:app --reload --port 8000
# -------------------------------------------------
audio_file = pathlib.Path(r"C:\Users\rishi\Downloads\sample.mpeg")

b64 = base64.b64encode(audio_file.read_bytes()).decode()
payload = {
    "audio_base64": b64,
    "mime_type":   "audio/mpeg",
    "language":    "auto",
    "latitude":    17.3850,
    "longitude":   78.4867,
}
resp = requests.post(
    "http://127.0.0.1:8000/api/emergency/audio-sos",
    json=payload,
    timeout=120,
)
result = resp.json()

# Save full response to a UTF-8 file (avoids Windows console encoding issues)
out_file = pathlib.Path(r"C:\Users\rishi\Sanjeeveni\Sanjeeveni-main\backend\test_result.json")
out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print(f"  STATUS:    {resp.status_code}")
print(f"  CASE ID:   {result.get('case_id', 'N/A')}")
print(f"  LANGUAGE:  {result.get('detected_language', 'N/A')}")
print(f"  CATEGORY:  {result.get('category', 'N/A')}")
print(f"  SEVERITY:  {result.get('severity', 'N/A')}")
print(f"  TRIAGE:    {result.get('triage_code', 'N/A')}")
print(f"  SPECIALTY: {result.get('recommended_doctor_specialty', 'N/A')}")
print(f"  TRANSLATED:{result.get('translated_english', 'N/A')}")
print("=" * 60)
print(f"✅ Full JSON successfully saved to: {out_file}")

