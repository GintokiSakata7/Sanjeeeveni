# How to Run AERO Mobile App on Android Phone (USB Debugging) 📱

Complete guide to running and debugging the Flutter mobile application directly on your connected physical Android phone without needing Android Studio IDE open.

---

## ⚡ Quick Start (Commands)

Open **PowerShell** or **Command Prompt** in the project root:

```cmd
# 1. Route phone requests to your PC backend (port 8000)
"C:\Users\This PC\AppData\Local\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000

# 2. Go to the mobile-app directory
cd "c:\Users\This PC\OneDrive\Desktop\akatsuki\Akatsuki\mobile-app"

# 3. Launch the app on your connected phone
flutter run
```
*(Or specify the target device directly: `flutter run -d 3bdcdeb7`)*

---

## 🛠️ System Configuration Reference

| Component | Path on this PC |
| :--- | :--- |
| **Flutter SDK** | `C:\src\flutter\bin\flutter.bat` |
| **Java JDK 17** | `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot` |
| **Android SDK** | `C:\Users\This PC\AppData\Local\Android\Sdk` |
| **ADB Executable** | `C:\Users\This PC\AppData\Local\Android\Sdk\platform-tools\adb.exe` |

---

## 📋 Step-by-Step Instructions

### Step 1: Connect Phone via USB
1. Plug your Android device into your PC with a USB cable.
2. Enable **Developer Options** and turn on **USB Debugging** on the phone.
3. Unlock your phone screen and tap **"Always allow from this computer"** on the popup.
4. Verify the connection by running:
   ```cmd
   adb devices
   ```
   You should see your device listed as `device` (e.g., `3bdcdeb7 device`).

---

### Step 2: Enable ADB Reverse Port
To allow the mobile app on your phone to reach the FastAPI backend on your PC (`http://127.0.0.1:8000`):
```cmd
adb reverse tcp:8000 tcp:8000
```
> 💡 *With `adb reverse`, your phone sends requests through the USB cable directly to localhost:8000 on your PC — no Wi-Fi IP configuration needed!*

---

### Step 3: Run the Flutter App
```cmd
cd mobile-app
flutter run
```

### Hot Reload / Hot Restart Controls (While Running):
- Press **`r`** in terminal — **Hot Reload** (instant UI update)
- Press **`R`** in terminal — **Hot Restart** (full app restart)
- Press **`q`** in terminal — **Quit / Detach**

---

## 🔧 Important Gradle Configuration

If you ever rebuild the Android project, ensure `mobile-app/android/gradle.properties` contains:
```properties
org.gradle.java.home=C:\\Program Files\\Eclipse Adoptium\\jdk-17.0.20.8-hotspot
```
This forces Gradle to use Adoptium OpenJDK 17 with valid SSL truststore certificates.
