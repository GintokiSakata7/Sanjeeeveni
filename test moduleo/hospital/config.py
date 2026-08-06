"""
Adaptive Smart Radar Navigator - Configuration Module (Hospital & Disease Edition)
Defines visual HUD colors, radar geometry, disease/symptom category mappings, and API endpoints.
"""

import pygame

# Window & Screen Layout
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 760
FPS = 60

# Radar Canvas Geometry
RADAR_CENTER_X = 420
RADAR_CENTER_Y = 380
RADAR_RADIUS_PX = 320

# UI Panel Layout
TELEMETRY_PANEL_X = 780
TELEMETRY_PANEL_Y = 20
TELEMETRY_PANEL_WIDTH = 480
TELEMETRY_PANEL_HEIGHT = 720

# Color Palette (Futuristic Neon Tactical HUD)
COLOR_BG = (8, 14, 18)                  # Deep Tactical Dark
COLOR_PANEL_BG = (12, 22, 28)            # Semi-transparent HUD Panel
COLOR_PANEL_BORDER = (24, 60, 50)        # Dark Cyan Frame Border

COLOR_RADAR_GRID = (0, 60, 40)           # Dark Muted Green Grid
COLOR_RADAR_RING = (0, 140, 80)          # Glowing Concentric Ring
COLOR_RADAR_SWEEP = (0, 255, 140)        # Bright Neon Green Sweep Line
COLOR_SWEEP_ARC = (0, 200, 100, 30)       # Semi-transparent Sector Alpha Arc

COLOR_TEXT_PRIMARY = (0, 255, 180)       # Neon Cyan Primary Text
COLOR_TEXT_SECONDARY = (140, 200, 190)    # Muted Teal Secondary Text
COLOR_TEXT_MUTED = (70, 110, 100)        # Dark Tactical Text
COLOR_ACCENT_WARN = (255, 180, 0)        # Amber Warning Yellow
COLOR_ACCENT_ALERT = (255, 50, 70)        # Tactical Red Alert

COLOR_TARGET_NORMAL = (0, 230, 130)      # Standard Hospital Green
COLOR_TARGET_LOCKED = (255, 60, 100)     # Locked Hospital Neon Crimson
COLOR_TARGET_RING = (0, 255, 200)        # Target Pulse Ring

# Adaptive Radius Steps (in meters) — starts at 50m, expands until hospital accepts
RADIUS_STEPS = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]

# Accept / Reject Button Colors (Hospital Response UI)
COLOR_BTN_ACCEPT = (0, 200, 100)            # Green accept button
COLOR_BTN_ACCEPT_HOVER = (0, 255, 140)      # Bright green hover
COLOR_BTN_REJECT = (220, 50, 60)            # Red reject button
COLOR_BTN_REJECT_HOVER = (255, 80, 100)     # Bright red hover
COLOR_RESPONSE_ACCEPTED = (0, 255, 140)     # Hospital accepted status
COLOR_RESPONSE_REJECTED = (255, 60, 80)     # Hospital rejected status
COLOR_RESPONSE_PENDING = (255, 180, 0)      # Hospital pending status
COLOR_FINAL_BANNER_BG = (10, 35, 30)        # Final selection banner background
COLOR_FINAL_BANNER_BORDER = (0, 255, 180)   # Final selection banner border

# Disease & Symptom Keyword Mapping Engine
DISEASE_KEYWORDS = {
    "ear": {"query": "ENT hospital", "specialty": "ENT / Ear, Nose & Throat", "diseases": ["Ear Infection", "Hearing Loss", "Otitis", "ENT Surgery"]},
    "ent": {"query": "ENT hospital", "specialty": "ENT / Otolaryngology", "diseases": ["Ear Care", "Throat", "Sinusitis", "Nose Disorders"]},
    "heart": {"query": "cardiology hospital", "specialty": "Cardiology & Heart Care", "diseases": ["Heart Failure", "Cardiac Arrest", "Angioplasty", "Chest Pain"]},
    "cardio": {"query": "cardiology hospital", "specialty": "Cardiology", "diseases": ["Heart Attack", "Hypertension", "Arrhythmia"]},
    "eye": {"query": "eye hospital", "specialty": "Ophthalmology / Eye Care", "diseases": ["Cataract", "Glaucoma", "Retina Care", "Vision Loss"]},
    "cancer": {"query": "cancer hospital", "specialty": "Oncology", "diseases": ["Chemotherapy", "Tumor Care", "Radiation Therapy", "Leukemia"]},
    "kidney": {"query": "kidney hospital", "specialty": "Nephrology & Urology", "diseases": ["Kidney Dialysis", "Renal Failure", "Kidney Stone", "Transplant"]},
    "bone": {"query": "orthopedic hospital", "specialty": "Orthopedics", "diseases": ["Fracture", "Joint Replacement", "Spine Care", "Bone Trauma"]},
    "ortho": {"query": "orthopedic hospital", "specialty": "Orthopedics", "diseases": ["Joint Pain", "Fracture", "Arthritis", "Bone Trauma"]},
    "child": {"query": "children hospital", "specialty": "Pediatrics", "diseases": ["Child Care", "Neonatal ICU", "Infant Fever", "Pediatric Care"]},
    "teeth": {"query": "dental hospital", "specialty": "Dental Care", "diseases": ["Tooth Pain", "Dental Surgery", "Root Canal"]},
    "dental": {"query": "dental hospital", "specialty": "Dental Care", "diseases": ["Tooth Extraction", "Implants", "Cavity"]},
    "skin": {"query": "dermatology hospital", "specialty": "Dermatology", "diseases": ["Skin Infection", "Allergy", "Eczema"]},
    "fever": {"query": "general hospital", "specialty": "General Emergency Medicine", "diseases": ["High Fever", "Viral Infection", "Dengue", "Typhoid"]},
}

# Auto-Refresh Interval
AUTO_REFRESH_INTERVAL = 30.0  # Seconds
