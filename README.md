# AERO – AI Emergency Response Orchestrator 🚨

AERO is an AI-powered emergency coordination platform designed to drastically reduce emergency response times. It integrates real-time speech-to-text intake, multilingual processing (English, Telugu, Hindi), AI triage severity classification, immediate step-by-step first-aid guidance, and response orchestration across Web and Mobile applications.

---

## 🏗️ Project Architecture & Directory Structure

```text
Akatsukibot/
├── backend/                  # FastAPI + SQLModel + AI Engine Backend
│   ├── database.py          # SQLModel PostgreSQL Engine & Session Manager
│   ├── db_models.py         # Pure Python SQLModel ORM Tables & Pydantic API Schemas
│   ├── services/
│   │   ├── whisper_service.py   # Groq Whisper Large v3 STT Transcriber
│   │   ├── triage_service.py    # AI Clinical Triage & Multilingual First-Aid Engine
│   │   └── responder_service.py # Hospital & Ambulance Allocation Engine
│   ├── .env                 # Environment variables (DB, Supabase, Groq, Gemini)
│   ├── ai_engine.py         # Main AI Orchestrator Pipeline
│   ├── main.py              # FastAPI Application Endpoints & Database Initializer
│   └── requirements.txt     # Python Dependencies
├── mobile-app/               # Expo React Native Mobile Application
│   ├── src/                 # Mobile API Client Service & Components
│   ├── App.js               # Root React Native SOS Screen
│   ├── app.json             # Expo Project Configuration
│   ├── metro.config.js      # Metro Bundler Config
│   ├── package.json         # Expo Dependencies
│   └── README.md            # Mobile Setup Guide
├── web-frontend/             # Vite + React Web Application
│   ├── src/
│   │   ├── components/      # Header, VoiceIntakeCard, GpsRadarMap, TriageResultCard
│   │   ├── pages/           # CitizenSosPage.jsx
│   │   ├── services/api.js  # Web API Client (localhost:8000)
│   │   ├── App.jsx          # React Root Component
│   │   └── index.css        # Executive Medical Light-Theme Styling
│   ├── package.json         # Node Dependencies
│   └── vite.config.js       # Vite Configuration
├── roadmap.md                # System Architecture & Development Blueprint
└── README.md                # Setup & Installation Guide
```

---

## 📋 Prerequisites

Before setting up AERO, ensure you have installed:
- **Python** (v3.10 or higher) & `pip`
- **Node.js** (v18.0.0 or higher) & `npm` / `npx`
- **Git**
- **PostgreSQL Database** (e.g. Supabase or local PostgreSQL)

---

## 🛠️ Step-by-Step Setup Guide

### 1. Environment Configuration

Create `.env` in `backend/` (`backend/.env`):
```env
# Database Connection (Supabase / PostgreSQL)
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres"

# Supabase Credentials
SUPABASE_URL="https://[YOUR-REF].supabase.co"
SUPABASE_KEY="your-supabase-service-role-key"

# AI & LLM Keys
GEMINI_API_KEY="your-gemini-api-key"
GROQ_API_KEY="your-groq-api-key"
```

---

### 2. Python Backend Setup (FastAPI + SQLModel)

Open a terminal window and launch the FastAPI server:

#### Windows (PowerShell):
```powershell
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Linux / macOS:
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The FastAPI backend runs at **`http://localhost:8000`** (Docs at `http://localhost:8000/docs`).

---

### 3. React Web Frontend Setup (`web-frontend/`)

Open a new terminal window, navigate to `web-frontend/`, install dependencies, and start Vite:

```bash
cd web-frontend
npm install
npm run dev
```

The React Citizen SOS web app will run at **`http://localhost:3000`**.

---

### 4. Expo Mobile App Setup (`mobile-app/`)

Open a new terminal window, navigate to `mobile-app/`, install dependencies, and start Expo:

```bash
cd mobile-app
npm install
```

#### 📱 How to Run:
- **Physical Phone (Expo Go)**: `npx expo start --tunnel` (Scan QR code with Expo Go app)
- **Web Browser (PC)**: `npx expo start --web` (Opens at `http://localhost:8081`)
- **Android Emulator**: `npx expo start --android`

---

## ⚡ Commands Summary Cheat Sheet

| Application | Command | Directory | Target |
| :--- | :--- | :--- | :--- |
| **FastAPI Backend** | `uvicorn main:app --reload --port 8000` | `backend/` | `http://localhost:8000` |
| **React Web App** | `npm run dev` | `web-frontend/` | `http://localhost:3000` |
| **Mobile App (Phone)**| `npx expo start --tunnel` | `mobile-app/` | Physical Phone via Expo Go QR |
| **Mobile App (Web)** | `npx expo start --web` | `mobile-app/` | `http://localhost:8081` |

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status and documentation links |
| `GET` | `/api/emergency/health` | Health check endpoint |
| `POST` | `/api/emergency/sos` | Text/transcript intake, language detection, translation, triage classification |
| `POST` | `/api/emergency/audio-sos` | Base64 audio file intake with Whisper Large v3 / Gemini 1.5 transcription & triage |
| `GET` | `/api/emergency/cases` | List active emergency cases directly from PostgreSQL |
