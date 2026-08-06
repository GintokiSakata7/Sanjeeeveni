# Adaptive Smart Radar Person Detection System

An interactive Python & Pygame based simulation of an **Adaptive Smart Radar Person Detection System** enforcing real-time sweep-fetch target validation, dynamic sweep scanning, target tracking, and visual telemetry animations.

---

## 📡 Overview & Features

* **Real-time Radar Sweep:** Simulates a 360° rotating radar beam scanning for targets within dynamic radial boundaries.
* **Sweep Fetch Validation:** Ensures target YES confirmations are strictly permitted only when the active radar sweep beam physically intersects and fetches the target.
* **Adaptive Radius Manager:** Automatically expands detection radius dynamically when full sweeps yield no detections.
* **Target Detection & Tracking:** Identifies, locks on to, and tracks moving simulated targets across radar sweeps.
* **Audio-Visual Feedback:** Synthesizes high-tech sonar pings (`Pygame` + `NumPy`) and dynamic UI animations (`AnimationManager`).

---

## 📁 Module Structure

```text
test moduleo/radar/
├── main.py                # Main Pygame application entry point
├── config.py              # Configuration settings & UI color palettes
├── radar.py               # Radar canvas & coordinate system
├── radar_sweep.py         # 360° sweep beam rotation & angle calculations
├── radius_manager.py      # Dynamic radial expansion & scaling logic
├── scanner_thread.py      # Multi-threaded background radar scanner loop
├── detector.py            # Signal detection & sweep intersection logic
├── tracker.py             # Target tracking, history & state management
├── target.py              # Simulated target provider & movement generator
├── animation_manager.py   # Visual pulse, ring, and lock animations
├── ui.py                  # Pygame UI HUD, telemetry display & rendering
└── README.md              # Documentation for the Radar Test Module
```

---

## ⚙️ Prerequisites & Dependencies

Ensure Python 3.10+ is installed along with the required libraries:

```bash
pip install pygame numpy
```

---

## 🚀 How to Run

To launch the Radar simulation, navigate to this directory and run `main.py`:

```bash
cd "test moduleo/radar"
python main.py
```

---

## 🛠️ Key Components Breakdown

| File | Description |
| :--- | :--- |
| **`main.py`** | Initializes Pygame window, event loop, sonar sound synthesizer, and main controller loop. |
| **`radar_sweep.py`** | Handles continuous rotational sweep math and angle tracking. |
| **`scanner_thread.py`** | Executes background thread scanning to prevent UI freezing. |
| **`radius_manager.py`** | Manages scale limits (e.g. 50m to 500m) and auto-expansion routines. |
| **`detector.py` & `tracker.py`** | Evaluates beam intersection and updates target locks. |
| **`ui.py` & `animation_manager.py`** | Renders HUD overlays, telemetry data, and visual animations. |
