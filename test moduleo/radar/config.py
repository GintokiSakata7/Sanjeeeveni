"""
Adaptive Smart Radar Person Detection System
Global Configuration & Constants
"""

# Screen & Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Adaptive Smart Radar - Person Detection System (Multi-Target YES/NO)"

# Radar Layout & Dimensions
RADAR_CENTER_X = 460
RADAR_CENTER_Y = 360
RADAR_PIXEL_RADIUS = 310  # Max pixel radius for scope display

# Search Range Settings (Meters)
INITIAL_RADIUS_METERS = 50.0
RADIUS_STEP_METERS = 50.0
MAX_RADIUS_METERS = 500.0

# Sweep & Physics Settings (FASTER SCANNING RATE)
SWEEP_SPEED_DEG_PER_FRAME = 4.2  # High-speed sweep (~1.4s per 360° turn at 60 FPS)
SWEEP_ARC_DEGREES = 45.0         # Arc angle of fading trail sector

# Color Palette (RGB / RGBA)
BG_COLOR = (6, 12, 20)             # Tactical Dark Navy
PANEL_BG = (10, 20, 32, 230)       # Glassmorphism Semi-transparent Dark Panel
PANEL_BORDER = (0, 180, 100)       # Neon Panel Border

RADAR_GREEN = (0, 255, 102)        # Primary Glowing Emerald
RADAR_DARK_GREEN = (0, 70, 35)     # Circle Grid Lines
RADAR_GRID_SUBTLE = (0, 45, 25)    # Minor Grid Lines
SWEEP_LINE_COLOR = (0, 255, 180)   # High-Speed Sweeping Beam Front

# Multi-Target Verification Palette
TARGET_PENDING = (255, 200, 0)     # Unverified Candidate Target (Amber/Yellow)
TARGET_YES = (0, 255, 102)         # Confirmed Person Target (Neon Green)
TARGET_NO = (100, 110, 120)        # Rejected / False Alarm (Muted Gray)
TARGET_SHORTEST_LOCK = (255, 40, 60)# Primary Shortest Distance Target Lock (Neon Crimson)

TEXT_PRIMARY = (0, 255, 102)       # Neon Green Text
TEXT_CYAN = (0, 229, 255)          # Tech Cyan
TEXT_ALERT = (255, 50, 70)         # Red Warning Text
TEXT_WARN = (255, 190, 40)         # Amber Caution Text
TEXT_MUTED = (100, 150, 130)       # Subdued Gray-Green Text

ACTIVE_RADIUS_RING_COLOR = (0, 229, 255) # Cyan highlight for current active search ring
TRACKING_VECTOR_COLOR = (255, 40, 60, 220)

ENABLE_AUDIO = True
