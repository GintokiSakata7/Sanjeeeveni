import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Search, Crosshair, Layers, Check, Loader2 } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet Default Icon Path Issues in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom Red Hospital Marker Pin
const redHospitalIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const TILE_SERVERS = {
  VOYAGER: {
    name: 'Street View',
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
  },
  DARK: {
    name: 'Dark Command View',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
  },
  OSM: {
    name: 'Standard OSM View',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }
};

const CITY_PRESETS = [
  { name: 'Banjara Hills', lat: 17.4126, lng: 78.4482 },
  { name: 'Jubilee Hills', lat: 17.4319, lng: 78.4071 },
  { name: 'Gachibowli', lat: 17.4401, lng: 78.3489 },
  { name: 'Hitec City', lat: 17.4435, lng: 78.3772 },
  { name: 'Secunderabad', lat: 17.4399, lng: 78.4983 },
  { name: 'Charminar', lat: 17.3616, lng: 78.4747 }
];

export default function LocationPickerMap({ latitude, longitude, onLocationChange }) {
  const [currentLat, setCurrentLat] = useState(latitude || 17.4126);
  const [currentLng, setCurrentLng] = useState(longitude || 78.4482);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [mapStyle, setMapStyle] = useState('VOYAGER');
  const [showStyleMenu, setShowStyleMenu] = useState(false);
  const [addressPreview, setAddressPreview] = useState('');

  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerInstanceRef = useRef(null);
  const tileLayerRef = useRef(null);

  // Initialize Real Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [currentLat, currentLng],
        zoom: 14,
        zoomControl: true
      });

      const tileConfig = TILE_SERVERS[mapStyle];
      const tileLayer = L.tileLayer(tileConfig.url, {
        attribution: tileConfig.attribution,
        maxZoom: 19
      }).addTo(map);

      // Add Draggable Red Hospital Marker
      const marker = L.marker([currentLat, currentLng], {
        icon: redHospitalIcon,
        draggable: true
      }).addTo(map);

      // Handle Marker Drag
      marker.on('dragend', (e) => {
        const coord = e.target.getLatLng();
        const newLat = parseFloat(coord.lat.toFixed(6));
        const newLng = parseFloat(coord.lng.toFixed(6));
        setCurrentLat(newLat);
        setCurrentLng(newLng);
        onLocationChange(newLat, newLng);
      });

      // Handle Map Click to Place Pin
      map.on('click', (e) => {
        const newLat = parseFloat(e.latlng.lat.toFixed(6));
        const newLng = parseFloat(e.latlng.lng.toFixed(6));
        setCurrentLat(newLat);
        setCurrentLng(newLng);
        marker.setLatLng([newLat, newLng]);
        onLocationChange(newLat, newLng);
      });

      mapInstanceRef.current = map;
      markerInstanceRef.current = marker;
      tileLayerRef.current = tileLayer;
    }
  }, []);

  // Update Tile Layer on Style Change
  useEffect(() => {
    if (mapInstanceRef.current && tileLayerRef.current) {
      const tileConfig = TILE_SERVERS[mapStyle];
      tileLayerRef.current.setUrl(tileConfig.url);
    }
  }, [mapStyle]);

  // Sync Marker & Map View when Lat/Lng changes externally
  const updateMapPosition = (lat, lng) => {
    setCurrentLat(lat);
    setCurrentLng(lng);
    if (mapInstanceRef.current && markerInstanceRef.current) {
      markerInstanceRef.current.setLatLng([lat, lng]);
      mapInstanceRef.current.setView([lat, lng], 15, { animate: true });
    }
    onLocationChange(lat, lng);
  };

  // Search Address using Nominatim Geocoding API
  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);

    try {
      const endpoint = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`;
      const res = await fetch(endpoint);
      const data = await res.json();

      if (data && data.length > 0) {
        const firstResult = data[0];
        const newLat = parseFloat(parseFloat(firstResult.lat).toFixed(6));
        const newLng = parseFloat(parseFloat(firstResult.lon).toFixed(6));
        setAddressPreview(firstResult.display_name);
        updateMapPosition(newLat, newLng);
      } else {
        alert(`No location results found for "${searchQuery}". Please try another search term.`);
      }
    } catch (err) {
      console.warn('Geocoding search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Detect User GPS Location
  const handleDetectLocation = () => {
    setIsLocating(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const newLat = parseFloat(pos.coords.latitude.toFixed(6));
          const newLng = parseFloat(pos.coords.longitude.toFixed(6));
          updateMapPosition(newLat, newLng);
          setIsLocating(false);
        },
        () => {
          setIsLocating(false);
          alert('Unable to access GPS location. Please check browser location permissions.');
        }
      );
    } else {
      setIsLocating(false);
    }
  };

  return (
    <div className="real-map-picker-card font-sans">
      {/* Top Header & Search Bar */}
      <div className="real-map-header">
        <div className="real-map-title">
          <MapPin size={20} className="text-red-500 shrink-0" />
          <div>
            <h4>Interactive Hospital Location Map</h4>
            <p>Drag the red pin or click anywhere on the real map to mark your hospital</p>
          </div>
        </div>

        <div className="real-map-actions">
          {/* Map Layer Style Switcher Button */}
          <div className="map-style-dropdown-wrapper">
            <button
              type="button"
              className="btn-map-style"
              onClick={() => setShowStyleMenu(!showStyleMenu)}
            >
              <Layers size={14} />
              <span>{TILE_SERVERS[mapStyle].name}</span>
            </button>

            {showStyleMenu && (
              <div className="map-style-menu">
                {Object.keys(TILE_SERVERS).map((key) => (
                  <button
                    key={key}
                    type="button"
                    className={`style-menu-item ${mapStyle === key ? 'active' : ''}`}
                    onClick={() => {
                      setMapStyle(key);
                      setShowStyleMenu(false);
                    }}
                  >
                    <span>{TILE_SERVERS[key].name}</span>
                    {mapStyle === key && <Check size={14} className="text-cyan-400" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            type="button"
            className="btn-locate"
            onClick={handleDetectLocation}
            disabled={isLocating}
          >
            <Crosshair size={14} className={isLocating ? 'animate-spin' : ''} />
            {isLocating ? 'Locating GPS...' : 'Use My GPS Location'}
          </button>
        </div>
      </div>

      {/* Address Geocoding Search Bar */}
      <form onSubmit={handleSearchSubmit} className="map-search-bar mt-3 mb-3">
        <div className="search-input-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search city, area, hospital landmark (e.g., Banjara Hills, Hyderabad)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="btn-search-map" disabled={isSearching}>
            {isSearching ? <Loader2 size={14} className="animate-spin" /> : 'Search Map'}
          </button>
        </div>
      </form>

      {addressPreview && (
        <div className="geocoded-address-bar mb-3">
          <span className="truncate">📍 Matched Location: {addressPreview}</span>
        </div>
      )}

      {/* Real Leaflet Map Container */}
      <div className="real-map-container-box">
        <div ref={mapContainerRef} className="leaflet-map-element" />
      </div>

      {/* Lat/Lng Inputs & City Presets */}
      <div className="coords-row mt-3">
        <div className="coord-box">
          <label>Latitude Coordinates *</label>
          <input
            type="number"
            step="0.000001"
            value={currentLat}
            onChange={(e) => {
              const val = parseFloat(e.target.value) || 0;
              updateMapPosition(val, currentLng);
            }}
          />
        </div>

        <div className="coord-box">
          <label>Longitude Coordinates *</label>
          <input
            type="number"
            step="0.000001"
            value={currentLng}
            onChange={(e) => {
              const val = parseFloat(e.target.value) || 0;
              updateMapPosition(currentLat, val);
            }}
          />
        </div>
      </div>

      {/* Quick Location Presets */}
      <div className="location-presets font-sans mt-3">
        <span className="preset-label">Quick Regional Presets:</span>
        <div className="preset-chips">
          {CITY_PRESETS.map((preset) => (
            <button
              key={preset.name}
              type="button"
              className={`preset-chip ${currentLat === preset.lat ? 'active' : ''}`}
              onClick={() => updateMapPosition(preset.lat, preset.lng)}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
