// AERO Citizen SOS Client Logic
const API_BASE_URL = "http://localhost:8000/api/emergency";

let currentLang = "en-US";
let currentMode = "voice";
let isListening = false;
let recognition = null;
let currentLatitude = 17.3850;
let currentLongitude = 78.4867;
let currentFirstAidSteps = [];

// Initialize Page
document.addEventListener("DOMContentLoaded", () => {
    initGeolocation();
    initSpeechRecognition();
    setupLanguageSelector();
});

// Setup Geolocation
function initGeolocation() {
    const gpsStatusText = document.getElementById("gps-status-text");
    const gpsCoords = document.getElementById("gps-coords");

    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                currentLatitude = pos.coords.latitude;
                currentLongitude = pos.coords.longitude;
                gpsStatusText.innerText = "GPS Location Active";
                gpsCoords.innerText = `Lat: ${currentLatitude.toFixed(4)}, Lng: ${currentLongitude.toFixed(4)}`;
            },
            (err) => {
                gpsStatusText.innerText = "GPS Fixed (Default Hyderabad)";
                gpsCoords.innerText = `Lat: ${currentLatitude.toFixed(4)}, Lng: ${currentLongitude.toFixed(4)}`;
            }
        );
    }
}

// Setup Language Selector
function setupLanguageSelector() {
    const langBtns = document.querySelectorAll(".lang-btn");
    langBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            langBtns.forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            currentLang = btn.getAttribute("data-lang");

            // Update recognition language if active
            if (recognition) {
                recognition.lang = currentLang;
            }

            // Update placeholder prompt
            const textarea = document.getElementById("voice-transcript");
            if (currentLang === "te-IN") {
                textarea.placeholder = "మీ అత్యవసర సమస్యను ఇక్కడ చెప్పండి (ఉదా: గుండె నొప్పిగా ఉంది, యాక్సిడెంట్ అయింది)...";
            } else if (currentLang === "hi-IN") {
                textarea.placeholder = "अपनी आपातकालीन स्थिति यहाँ बोलें (उदा: छाती में तेज दर्द, एक्सीडेंट)...";
            } else {
                textarea.placeholder = "Your spoken speech will appear here automatically... Or tap microphone above.";
            }
        });
    });
}

// Switch Input Modes (Voice vs Type)
function switchMode(mode) {
    currentMode = mode;
    document.getElementById("tab-voice").classList.toggle("active", mode === "voice");
    document.getElementById("tab-type").classList.toggle("active", mode === "type");

    document.getElementById("section-voice").classList.toggle("hidden", mode !== "voice");
    document.getElementById("section-type").classList.toggle("hidden", mode !== "type");
}

// Speech Recognition (Web Speech API)
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        document.getElementById("mic-status").innerText = "Web Speech API not supported in browser. Please use Type SOS.";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = currentLang;

    recognition.onstart = () => {
        isListening = true;
        document.getElementById("mic-btn").classList.add("listening");
        document.getElementById("mic-status").innerText = "🎙️ Listening... Speak clearly in your language.";
    };

    recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        document.getElementById("voice-transcript").value = transcript;
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        isListening = false;
        document.getElementById("mic-btn").classList.remove("listening");
        document.getElementById("mic-status").innerText = "Speech intake paused. Tap mic to retry.";
    };

    recognition.onend = () => {
        isListening = false;
        document.getElementById("mic-btn").classList.remove("listening");
    };
}

function toggleSpeech() {
    if (!recognition) return;
    if (isListening) {
        recognition.stop();
    } else {
        recognition.lang = currentLang;
        recognition.start();
    }
}

// Add Quick Chip Text
function addChip(text) {
    const typeTextarea = document.getElementById("type-text");
    typeTextarea.value = typeTextarea.value ? typeTextarea.value + ", " + text : text;
}

// Submit SOS Request to FastAPI Backend
async function submitSOS() {
    const textInput = currentMode === "voice" 
        ? document.getElementById("voice-transcript").value 
        : document.getElementById("type-text").value;

    if (!textInput || textInput.trim().length === 0) {
        alert("Please speak or type your emergency description before sending SOS.");
        return;
    }

    // Stop listening if active
    if (recognition && isListening) {
        recognition.stop();
    }

    // Show Loading
    document.getElementById("ai-loading").classList.remove("hidden");
    document.getElementById("triage-result-card").classList.add("hidden");

    try {
        const response = await fetch(`${API_BASE_URL}/sos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: textInput,
                input_mode: currentMode,
                language: currentLang,
                latitude: currentLatitude,
                longitude: currentLongitude
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned error status ${response.status}`);
        }

        const data = await response.json();

        // Render Triage Results
        renderTriageResults(data);

    } catch (err) {
        console.error("Error submitting SOS:", err);
        alert("Unable to reach AERO Emergency backend. Ensure FastAPI server is running on http://localhost:8000.");
    } finally {
        document.getElementById("ai-loading").classList.add("hidden");
    }
}

// Render Results Card
function renderTriageResults(data) {
    const card = document.getElementById("triage-result-card");
    const triage = data.triage;

    // Severity Pill & Header
    const severityPill = document.getElementById("result-severity-pill");
    severityPill.innerText = `🚨 ${triage.severity.replace('_', ' ')}`;
    
    document.getElementById("result-category").innerText = triage.category;
    document.getElementById("result-summary").innerText = triage.triage_summary;

    // Response Orchestration Details
    if (data.hospital) {
        document.getElementById("orch-hospital-name").innerText = data.hospital.name;
        document.getElementById("orch-hospital-eta").innerText = `Distance: ${data.hospital.distance_km} km • ETA: ${data.hospital.eta_minutes} mins`;
    }

    if (data.ambulance) {
        document.getElementById("orch-ambulance-veh").innerText = `${data.ambulance.vehicle_number} (${data.ambulance.equipment_level})`;
        document.getElementById("orch-ambulance-eta").innerText = `Arriving in ${data.ambulance.eta_minutes} mins • Driver: ${data.ambulance.driver_name}`;
    }

    document.getElementById("orch-doctor-spec").innerText = `${data.doctor_specialty} (On Standby)`;

    // First Aid List (Use Native language steps if available)
    const steps = (triage.first_aid_native && triage.first_aid_native.length > 0)
        ? triage.first_aid_native
        : triage.first_aid_english;
    
    currentFirstAidSteps = steps;

    const firstAidListEl = document.getElementById("first-aid-list");
    firstAidListEl.innerHTML = "";

    steps.forEach((step, idx) => {
        const stepDiv = document.createElement("div");
        stepDiv.className = "fa-step";
        stepDiv.innerHTML = `
            <div class="fa-num">${step.step_number || idx + 1}</div>
            <div>${step.icon || '⚠️'} ${step.instruction}</div>
        `;
        firstAidListEl.appendChild(stepDiv);
    });

    card.classList.remove("hidden");
    card.scrollIntoView({ behavior: "smooth" });
}

// Text to Speech Read Aloud
function readFirstAidAloud() {
    if (!currentFirstAidSteps || currentFirstAidSteps.length === 0) return;

    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel(); // Stop ongoing speech

        const fullText = currentFirstAidSteps.map(s => s.instruction).join(". ");
        const utterance = new SpeechSynthesisUtterance(fullText);
        utterance.lang = currentLang;
        utterance.rate = 0.9; // Slightly slower for emergency clarity

        window.speechSynthesis.speak(utterance);
    } else {
        alert("Text-to-speech audio reader is not supported in this browser.");
    }
}
