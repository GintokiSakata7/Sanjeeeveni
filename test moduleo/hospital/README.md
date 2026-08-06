# 🏥 Adaptive Smart Radar Navigator (Hospital & POI Radar)

A futuristic military-style tactical Pygame radar application that uses real-time GPS location and the OpenStreetMap Overpass API to locate nearby medical facilities, hospitals, and emergency services with **Adaptive Search Radius Expansion**.

---

## 📡 Key Features

* **Real-Time GPS Location Detection**: Detects user coordinates using `geocoder` and IP-API with offline fallback support.
* **Adaptive Search Radius Expansion**: Automatically scales search radius step-by-step (**500m → 1km → 2km → 5km → 10km → 20km → 50km**) until facilities are found.
* **Tactical 60 FPS Radar Visualization**: Concentric glowing radar rings, 360° rotating sweep beam line, transparent sweep sector arc, degree markings, crosshairs, and a mini compass.
* **Real-Time POI Integration**: Fetches real-world hospital names, coordinates, geodesic distance (meters/km), and compass bearings (0°–360°).
* **Target Lock & Sonar Ping Audio**: Synthesizes high-tech sonar sound effects using NumPy and Pygame Audio.
* **Multi-Category Support**: Seamlessly switch POI categories (`1: Hospitals`, `2: Police`, `3: Fire Stations`, `4: Pharmacies`, `5: EV Chargers`, `6: ATMs`).
* **Non-Blocking Multi-Threaded Architecture**: Non-freezing Pygame UI with background threads handling Overpass API network queries.
* **JSON Export & Caching**: Caches recent search results and automatically exports found targets to `found_hospitals.json`.

---

## 📁 Project Structure

```text
hospital/
├── main.py              # Main application entry point & 60 FPS Pygame loop
├── config.py            # HUD colors, layout geometry, search categories, & settings
├── gps_manager.py       # Real-time GPS coordinate resolver (Geocoder / IP-API)
├── hospital_search.py   # Overpass API parser, geodesic distance, & bearing calculations
├── radius_manager.py    # Adaptive radius expansion logic (500m -> 50km)
├── detector.py          # GPS-to-2D radar pixel coordinate projection & sweep intersection
├── radar.py             # 360° radar canvas renderer, sweep beam line, & mini compass
├── animation.py         # Tactical target reticles, shockwave rings, & sonar sound synthesizer
├── ui.py                # Telemetry HUD sidebar, target breakdown, & keyboard legends
├── requirements.txt     # Python package dependencies
└── README.md            # Documentation & setup instructions
```

---

## ⚙️ Installation & Setup

1. Navigate to the project directory:
```bash
cd "test moduleo/radar/hospital"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

Execute the main application script:

```bash
python main.py
```

---

## 🎮 Keyboard Controls

| Key | Action |
| :--- | :--- |
| **`SPACE`** | Trigger immediate Radar POI Search |
| **`1` .. `6`** | Switch Category (`1: Hospitals`, `2: Police`, `3: Fire`, `4: Pharmacy`, `5: EV`, `6: ATM`) |
| **`H`** | Quick-switch category to **Hospitals** and execute search |
| **`R`** | Reset Search Radius baseline back to **500m** |
| **`L`** | Refresh GPS location fix |
| **`ESC`** | Exit application |
