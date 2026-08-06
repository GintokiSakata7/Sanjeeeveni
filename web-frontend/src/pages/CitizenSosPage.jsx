import React, { useState, useEffect, useRef } from 'react';
import Header from '../components/Header';
import GpsRadarMap from '../components/GpsRadarMap';
import VoiceIntakeCard from '../components/VoiceIntakeCard';
import CategoryPresets from '../components/CategoryPresets';
import TriageResultCard from '../components/TriageResultCard';
import { sendSosRequest } from '../services/api';

export default function CitizenSosPage() {
  const [selectedLang, setSelectedLang] = useState("auto"); // "auto", "en-IN", "te-IN", "hi-IN"
  const [inputMode, setInputMode] = useState("voice"); // "voice" | "type"
  const [isListening, setIsListening] = useState(false);
  
  const [transcript, setTranscript] = useState("");
  const [typedText, setTypedText] = useState("");
  
  const [gps, setGps] = useState({ lat: 17.3850, lng: 78.4867, status: "GPS ACTIVE • HYDERABAD NODE" });
  const [loading, setLoading] = useState(false);
  const [triageResult, setTriageResult] = useState(null);

  const recognitionRef = useRef(null);
  const accumulatedRef = useRef("");

  // Initialize GPS Coordinates
  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGps({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            status: "GPS ACTIVE • HIGH ACCURACY"
          });
        },
        () => {
          setGps({
            lat: 17.3850,
            lng: 78.4867,
            status: "GPS FIXED • REGIONAL NODE"
          });
        }
      );
    }
  }, []);

  // Web Speech API: Real-Time Instant Speech-To-Text Streaming
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = selectedLang === "auto" ? "en-IN" : selectedLang;

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = (err) => {
        console.error("Speech Recognition Error:", err);
        setIsListening(false);
      };

      recognition.onresult = (event) => {
        let currentSessionFinal = "";
        let interimText = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const text = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            currentSessionFinal += text + " ";
          } else {
            interimText += text;
          }
        }

        if (currentSessionFinal) {
          accumulatedRef.current += currentSessionFinal;
        }

        setTranscript((accumulatedRef.current + " " + interimText).trim());
      };

      recognitionRef.current = recognition;
    }
  }, [selectedLang]);

  // Toggle Microphone Intake
  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Browser speech recognition unavailable. Please use Type SOS mode.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.lang = selectedLang === "auto" ? "en-IN" : selectedLang;
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.log("Recognition active");
      }
    }
  };

  // Add Quick Symptom Preset
  const addSymptomPreset = (chipText) => {
    setTypedText((prev) => (prev ? `${prev}, ${chipText}` : chipText));
    setInputMode("type");
  };

  // Clear Inputs
  const handleClear = () => {
    accumulatedRef.current = "";
    setTranscript("");
    setTypedText("");
    setTriageResult(null);
  };

  // Submit SOS Signal
  const submitSOS = async () => {
    const activeText = inputMode === "voice" ? transcript : typedText;

    if (!activeText || activeText.trim().length === 0) {
      alert("Please speak or type your emergency description before sending SOS.");
      return;
    }

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
    }

    setLoading(true);
    setTriageResult(null);

    try {
      const data = await sendSosRequest({
        text: activeText,
        input_mode: inputMode,
        language: selectedLang,
        latitude: gps.lat,
        longitude: gps.lng
      });

      setTriageResult(data);
    } catch (err) {
      console.error("Error submitting SOS:", err);
      alert("Unable to connect to AERO AI FastAPI server on http://localhost:8000.");
    } finally {
      setLoading(false);
    }
  };

  // Text-To-Speech Read Aloud
  const speakFirstAid = () => {
    if (!triageResult) return;

    const steps = (triageResult.first_aid_native && triageResult.first_aid_native.length > 0)
      ? triageResult.first_aid_native
      : triageResult.first_aid_english;

    if (!steps || steps.length === 0) return;

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const fullText = steps.map(s => s.instruction).join(". ");
      const utterance = new SpeechSynthesisUtterance(fullText);
      utterance.lang = triageResult.language_code || "en-US";
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="dashboard-root">
      <Header selectedLang={selectedLang} setSelectedLang={setSelectedLang} />

      <div className="dashboard-grid">
        <div className="intake-panel">
          <VoiceIntakeCard
            inputMode={inputMode}
            setInputMode={setInputMode}
            selectedLang={selectedLang}
            setSelectedLang={setSelectedLang}
            isListening={isListening}
            toggleListening={toggleListening}
            transcript={transcript}
            setTranscript={(val) => {
              accumulatedRef.current = val;
              setTranscript(val);
            }}
            typedText={typedText}
            setTypedText={setTypedText}
            handleClear={handleClear}
          />

          <CategoryPresets addSymptomPreset={addSymptomPreset} />

          <button className="big-sos-btn" onClick={submitSOS}>
            🚨 TRANSMIT SOS SIGNAL
          </button>
        </div>

        <div className="orchestrator-panel">
          <GpsRadarMap gps={gps} />

          <TriageResultCard
            triageResult={triageResult}
            loading={loading}
            speakFirstAid={speakFirstAid}
          />
        </div>
      </div>
    </div>
  );
}
