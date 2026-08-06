# AERO Mobile Application (Flutter) 📱

AERO Mobile is the official Android/iOS mobile application for the AI Emergency Response Orchestrator platform, built with **Flutter 3.44+**.

---

## 📋 Prerequisites

- **Flutter SDK** v3.44.0+ — https://flutter.dev/docs/get-started/install/windows
- **Android Studio** with Android SDK and a connected device or active emulator
- Verify setup with: `flutter doctor`

---

## 🚀 Setup & Run

### 1. Install Dependencies

> ⚠️ Run in **cmd.exe** (not PowerShell or Git Bash) on Windows.

```cmd
cd mobile-app
flutter pub get
```

---

### 2. Run the App

```cmd
flutter run
```

#### Options:
- **Physical Android Phone**: Connect via USB with USB Debugging enabled
- **Android Emulator**: Launch in Android Studio, then run `flutter run`
- **List available devices**: `flutter devices`

---

## 📡 Backend Connection

| Platform | FastAPI URL | Setup Note |
| :--- | :--- | :--- |
| Physical Device (USB) | `http://127.0.0.1:8000` | Run `adb reverse tcp:8000 tcp:8000` |
| Android Emulator | `http://10.0.2.2:8000` | Default emulator loopback |
| Physical Device (Wi-Fi) | `http://<PC_LOCAL_IP>:8000` | Same Wi-Fi network required |

See **[RUN_ON_MOBILE.md](file:///c:/Users/This%20PC/OneDrive/Desktop/akatsuki/Akatsuki/mobile-app/RUN_ON_MOBILE.md)** for the full guide.

---

## 📁 Project Structure

```text
mobile-app/
├── lib/
│   ├── main.dart                     # App entry point
│   ├── models/triage_result.dart     # TriageResult & FirstAidStep data models
│   ├── screens/citizen_sos_screen.dart  # Main Emergency Intake UI
│   └── services/api_service.dart    # HTTP client for FastAPI backend
└── pubspec.yaml                      # Flutter dependencies
```
