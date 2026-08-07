import { fetchWithFallback } from './apiClient';

/**
 * Sends SOS text payload to FastAPI backend
 */
export async function sendSosRequest(payload) {
  const response = await fetchWithFallback("/api/emergency/sos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Server returned status ${response.status}`);
  }

  return await response.json();
}

/**
 * Helper to convert Blob to Base64
 */
export function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result.split(',')[1];
      resolve(base64String);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Sends JSON Base64 audio payload to FastAPI backend
 */
export async function sendAudioSosRequest(audioBlob, language, latitude, longitude) {
  const base64Audio = await blobToBase64(audioBlob);

  const response = await fetchWithFallback("/api/emergency/audio-sos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      audio_base64: base64Audio,
      mime_type: audioBlob.type || "audio/webm",
      language: language,
      latitude: latitude,
      longitude: longitude
    })
  });

  if (!response.ok) {
    throw new Error(`Server returned audio status ${response.status}`);
  }

  return await response.json();
}

