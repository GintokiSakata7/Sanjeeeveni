import React, { useState, useEffect, useRef } from 'react';
import Header from '../components/Header';
import GpsRadarMap from '../components/GpsRadarMap';
import VoiceIntakeCard from '../components/VoiceIntakeCard';
import CategoryPresets from '../components/CategoryPresets';
import TriageResultCard from '../components/TriageResultCard';
import { sendSosRequest, sendAudioSosRequest } from '../services/api';
import RadarCanvas from '../components/RadarCanvas';
import HospitalResponsePanel from '../components/HospitalResponsePanel';
import LiveSOSTracker from '../components/LiveSOSTracker';
import useRadarSearch from '../hooks/useRadarSearch';
import useHelperSearch from '../hooks/useHelperSearch';
import HelperResponsePanel from '../components/HelperResponsePanel';
import { fetchWithFallback } from '../services/apiClient';

export default function CitizenSosPage({
  selectedLang: propSelectedLang,
  setSelectedLang: propSetSelectedLang,
  onOpenHospitalRegistration,
  onOpenHospitalLogin,
  onOpenAdminLogin
}) {
  const [internalLang, setInternalLang] = useState("auto");
  const selectedLang = propSelectedLang || internalLang;
  const setSelectedLang = propSetSelectedLang || setInternalLang;
  const notifiedHelpersRef = useRef(new Set());

  const [inputMode, setInputMode] = useState("voice"); // "voice" | "type"
  const [isListening, setIsListening] = useState(false);
  
  const [transcript, setTranscript] = useState("");
  const [typedText, setTypedText] = useState("");
  const [audioBlob, setAudioBlob] = useState(null);

  const [gps, setGps] = useState({ lat: 17.3850, lng: 78.4867, status: "GPS ACTIVE • HYDERABAD NODE" });
  const [loading, setLoading] = useState(false);
  const [triageResult, setTriageResult] = useState(null);

  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const accumulatedRef = useRef("");

  // Full radar search hooks
  const radar = useRadarSearch();
  const helperSearch = useHelperSearch();
  const [showRadarSection, setShowRadarSection] = useState(true);

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

  // Start MediaRecorder (Audio Binary Capture for Groq Whisper v3)
  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(250);
      mediaRecorderRef.current = mediaRecorder;
    } catch (err) {
      console.warn("MediaRecorder mic access not granted or unsupported:", err);
    }
  };

  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  // Toggle Microphone Intake (Web Speech + MediaRecorder)
  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch(e){}
      }
      stopAudioRecording();
      setIsListening(false);
    } else {
      setAudioBlob(null);
      accumulatedRef.current = "";
      setTranscript("");
      startAudioRecording();
      
      if (recognitionRef.current) {
        recognitionRef.current.lang = selectedLang === "auto" ? "en-IN" : selectedLang;
        try { recognitionRef.current.start(); } catch (e) {}
      } else {
        setIsListening(true);
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
    setAudioBlob(null);
    setTriageResult(null);
  };

  // Submit SOS Signal
  const submitSOS = async () => {
    if (isListening) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch(e){}
      }
      stopAudioRecording();
      setIsListening(false);
    }

    const activeText = inputMode === "voice" ? transcript : typedText;

    if (inputMode === "voice" && !audioBlob && (!activeText || activeText.trim().length === 0)) {
      alert("Please speak into the microphone or type your emergency description before transmitting SOS.");
      return;
    }

    if (inputMode === "type" && (!typedText || typedText.trim().length === 0)) {
      alert("Please type your emergency description before transmitting SOS.");
      return;
    }

    setLoading(true);
    setTriageResult(null);

    // Start both searches
    radar.startSearch(gps.lat, gps.lng, {
      text: activeText,
      latitude: gps.lat,
      longitude: gps.lng,
      urgency: 'HIGH' // default until AI says otherwise
    });
    
    // Start helper search in parallel
    helperSearch.startSearch(gps.lat, gps.lng);

    try {
      let data;
      // If we recorded audio, send high-precision audio blob to Whisper Large v3 backend
      if (inputMode === "voice" && audioBlob) {
        data = await sendAudioSosRequest(
          audioBlob,
          selectedLang,
          gps.lat,
          gps.lng
        );
      } else {
        // Text-based intake (or live transcript if mic failed)
        data = await sendSosRequest({
          text: activeText,
          input_mode: inputMode,
          language: selectedLang,
          latitude: gps.lat,
          longitude: gps.lng
        });
      }

      setTriageResult(data);
      // Update the radar payload with the confirmed AI urgency
      if (radar.updateSosPayload) {
        radar.updateSosPayload({ urgency: data.severity });
      }
    } catch (err) {
      console.error("Error submitting SOS:", err);
      alert("Unable to connect to AERO AI FastAPI server (tried local server and Render cloud fallback).");
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

  const routedSosIdForHelpers = radar.finalHospital
    ? radar.responses[`${radar.finalHospital.id}_sos_id`]
    : Object.entries(radar.responses).find(([key, value]) => key.endsWith('_sos_id') && value)?.[1];

  // Notify newly discovered helpers
  useEffect(() => {
    if (!routedSosIdForHelpers) return;
    
    helperSearch.discoveredHelpers.forEach(async (h) => {
      const helperId = String(h.id);
      if (!notifiedHelpersRef.current.has(helperId)) {
        notifiedHelpersRef.current.add(helperId);
        try {
          await fetchWithFallback('/api/v1/mobile/helper/notify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sos_id: routedSosIdForHelpers, helper_id: helperId })
          });
        } catch (err) {
          console.error("Failed to notify helper", err);
        }
      }
    });
  }, [routedSosIdForHelpers, helperSearch.discoveredHelpers]);

  // Poll Supabase for Helper Status
  useEffect(() => {
    if (!routedSosIdForHelpers) return;
    
    let intervalId = null;
    if (helperSearch.isSearchActive && !helperSearch.finalHelper) {
      intervalId = setInterval(async () => {
        try {
          const res = await fetchWithFallback(`/api/v1/routing/helper-status/${routedSosIdForHelpers}`);
          if (res.ok) {
            const data = await res.json();
            data.forEach(notif => {
              if (notif.status === 'ACCEPTED') {
                helperSearch.acceptHelper(notif.helper_id);
              } else if (notif.status === 'REJECTED') {
                helperSearch.rejectHelper(notif.helper_id);
              }
            });
          }
        } catch (err) {
          console.error("Error polling helper status:", err);
        }
      }, 3000);
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [routedSosIdForHelpers, helperSearch.isSearchActive, helperSearch.finalHelper, helperSearch.acceptHelper, helperSearch.rejectHelper]);

  // Prepare discovered IDs for radar canvas
  const discoveredIds = radar.discoveredHospitals.map(h => h.id);
  const discoveredHelperIds = helperSearch.discoveredHelpers.map(h => h.id);
  
  // Get SOS ID of accepted case
  const finalSosId = radar.finalHospital ? radar.responses[`${radar.finalHospital.id}_sos_id`] : null;

  return (
    <div className="dashboard-root">
      <Header
        selectedLang={selectedLang}
        setSelectedLang={setSelectedLang}
        onOpenHospitalRegistration={onOpenHospitalRegistration}
        onOpenHospitalLogin={onOpenHospitalLogin}
        onOpenAdminLogin={onOpenAdminLogin}
      />

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
            hasAudioBlob={!!audioBlob}
          />

          <CategoryPresets addSymptomPreset={addSymptomPreset} />

          <button className="big-sos-btn" onClick={submitSOS}>
            🚨 TRANSMIT SOS SIGNAL
          </button>

        </div>

        <div className="orchestrator-panel">
          <GpsRadarMap gps={gps} />

          {finalSosId && (
            <LiveSOSTracker sosId={finalSosId} />
          )}

          <TriageResultCard
            triageResult={triageResult}
            loading={loading}
            speakFirstAid={speakFirstAid}
          />
          
          <div className="toggle-switch-wrapper">
            <span className="toggle-switch-label">Live Radar & Helpers</span>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={showRadarSection} 
                onChange={() => setShowRadarSection(!showRadarSection)} 
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {showRadarSection && (
            <div className="radar-and-hospitals-section">
              {/* Hospital Response Panel — Left beside the radar */}
              <div className="hospital-panel-wrapper">
                <HospitalResponsePanel
                  discoveredHospitals={radar.discoveredHospitals}
                  responses={radar.responses}
                  onAccept={radar.acceptHospital}
                  onReject={radar.rejectHospital}
                  isSearchActive={radar.isSearchActive}
                  finalHospital={radar.finalHospital}
                  currentRadius={radar.currentRadius}
                  totalCount={radar.totalCount}
                  pendingCount={radar.pendingCount}
                  acceptedCount={radar.acceptedCount}
                  rejectedCount={radar.rejectedCount}
                  notifications={radar.notifications}
                />
              </div>

              {/* Radar Canvas — Middle */}
              <div className="radar-canvas-wrapper">
                <RadarCanvas
                  allHospitals={radar.allHospitals}
                  discoveredIds={discoveredIds}
                  responses={radar.responses}
                  currentRadius={Math.max(radar.currentRadius || 0, helperSearch.currentRadius || 0)}
                  maxRadius={radar.RADIUS_STEPS[radar.RADIUS_STEPS.length - 1]}
                  isScanning={radar.isSearchActive || helperSearch.isSearchActive}
                  onSweepDiscover={radar.discoverHospital}
                  getUndiscoveredInRadius={radar.getUndiscoveredInRadius}
                  finalHospitalId={radar.finalHospital ? radar.finalHospital.id : null}
                  allHelpers={helperSearch.allHelpers}
                  discoveredHelperIds={discoveredHelperIds}
                  helperResponses={helperSearch.responses}
                  onSweepDiscoverHelper={helperSearch.discoverHelper}
                  getUndiscoveredHelpersInRadius={helperSearch.getUndiscoveredInRadius}
                  finalHelperId={helperSearch.finalHelper ? helperSearch.finalHelper.id : null}
                />
              </div>

              {/* Helper Response Panel — Right beside the radar */}
              <div className="helper-panel-wrapper">
                <HelperResponsePanel
                  discoveredHelpers={helperSearch.discoveredHelpers}
                  responses={helperSearch.responses}
                  onAccept={helperSearch.acceptHelper}
                  onReject={helperSearch.rejectHelper}
                  isSearchActive={helperSearch.isSearchActive}
                  finalHelper={helperSearch.finalHelper}
                  currentRadius={helperSearch.currentRadius}
                  totalCount={helperSearch.totalCount}
                  pendingCount={helperSearch.pendingCount}
                  acceptedCount={helperSearch.acceptedCount}
                  rejectedCount={helperSearch.rejectedCount}
                  notifications={helperSearch.notifications}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
