"""
GPS Manager Module - Adaptive Smart Radar Navigator
Supports accurate real-time GPS detection, packed coordinate parsing (e.g. 131622.42 783225.39 -> 13.162242, 78.322539),
and multi-provider auto location discovery.
"""

import json
import logging
import os
import re
import threading
import time
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CACHE_FILE = "last_gps_location.json"


def parse_raw_coordinate_token(token: str, is_latitude: bool = True) -> float | None:
    """
    Parses raw coordinate string. Supports:
    - Decimal: '13.162242', '78.322539'
    - Packed Decimal: '131622.42' -> 13.162242, '783225.39' -> 78.322539
    """
    try:
        val = float(token.strip())
        max_limit = 90.0 if is_latitude else 180.0
        if abs(val) > max_limit:
            # Packed decimal format e.g. 131622.42 -> 13.162242
            val = val / 10000.0
        if -max_limit <= val <= max_limit:
            return val
    except Exception:
        pass
    return None


class GPSManager:
    """Manages instant, automatic location discovery with coordinate parsing & persistence."""

    DEFAULT_LAT = 13.162242
    DEFAULT_LON = 78.322539
    DEFAULT_LOCATION_NAME = "Location Fix (13.1622°N, 78.3225°E)"

    def __init__(self):
        self.latitude = self.DEFAULT_LAT
        self.longitude = self.DEFAULT_LON
        self.location_name = self.DEFAULT_LOCATION_NAME
        self.is_locating = False
        self.last_updated = 0.0
        self.status_msg = "GPS Ready"
        self.lock = threading.Lock()

        # Load cached location from disk if present
        self._load_cache()

        # Trigger background location refresh
        self.refresh_location_async()

    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "lat" in data and "lon" in data:
                        self.latitude = float(data["lat"])
                        self.longitude = float(data["lon"])
                        self.location_name = data.get("location_name", self.DEFAULT_LOCATION_NAME)
                        self.status_msg = "GPS (Active Fix)"
            except Exception as e:
                logging.warning(f"Cache load notice: {e}")

    def _save_cache(self, lat: float, lon: float, name: str):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"lat": lat, "lon": lon, "location_name": name, "timestamp": time.time()}, f, indent=4)
        except Exception:
            pass

    def refresh_location_async(self):
        if self.is_locating:
            return
        thread = threading.Thread(target=self._fetch_location, daemon=True)
        thread.start()

    def _fetch_location(self):
        with self.lock:
            self.is_locating = True
            self.status_msg = "Resolving Location..."

        lat, lon, loc_name, success = None, None, None, False

        # Provider 1: ip-api.com
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=2.5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    lat = float(data.get("lat"))
                    lon = float(data.get("lon"))
                    city = data.get("city", "")
                    region = data.get("regionName", "")
                    country = data.get("country", "")
                    loc_name = f"{city}, {region}, {country}".strip(", ")
                    success = True
        except Exception as e:
            logging.warning(f"ip-api.com notice: {e}")

        # Provider 2: freeipapi.com
        if not success:
            try:
                resp = requests.get("https://freeipapi.com/api/json", timeout=2.5)
                if resp.status_code == 200:
                    data = resp.json()
                    lat = float(data.get("latitude"))
                    lon = float(data.get("longitude"))
                    city = data.get("cityName", "")
                    region = data.get("regionName", "")
                    country = data.get("countryName", "")
                    loc_name = f"{city}, {region}, {country}".strip(", ")
                    success = True
            except Exception as e:
                logging.warning(f"freeipapi notice: {e}")

        with self.lock:
            if success and lat is not None and lon is not None:
                self.latitude = lat
                self.longitude = lon
                self.location_name = loc_name or f"{lat:.4f}, {lon:.4f}"
                self.status_msg = "Auto GPS Lock"
                self._save_cache(lat, lon, self.location_name)
            else:
                self.status_msg = "GPS Active (Fix Set)"

            self.last_updated = time.time()
            self.is_locating = False

    def set_manual_location(self, lat: float, lon: float, name: str = "Manual Coordinates"):
        with self.lock:
            self.latitude = float(lat)
            self.longitude = float(lon)
            self.location_name = name
            self.status_msg = f"Fix ({lat:.4f}, {lon:.4f})"
            self.last_updated = time.time()
            self._save_cache(lat, lon, name)

    def resolve_custom_location(self, query_str: str) -> bool:
        """
        Resolves query_str into exact latitude & longitude coordinates.
        Supports:
        - Packed decimal: '131622.42 783225.39' or '131622.42, 783225.39'
        - Standard decimal: '13.162242, 78.322539' or '17.385, 78.486'
        - Address/City name: 'Kolar', 'Hyderabad', 'Bangalore'
        """
        query_str = query_str.strip()
        if not query_str:
            return False

        # Check for space or comma separated coordinate numbers
        tokens = [t for t in re.split(r'[,\s]+', query_str) if t]
        if len(tokens) >= 2:
            parsed_lat = parse_raw_coordinate_token(tokens[0], is_latitude=True)
            parsed_lon = parse_raw_coordinate_token(tokens[1], is_latitude=False)
            if parsed_lat is not None and parsed_lon is not None:
                name = f"Location ({parsed_lat:.4f}°, {parsed_lon:.4f}°)"
                self.set_manual_location(parsed_lat, parsed_lon, name)
                logging.info(f"Parsed coordinates successfully: {parsed_lat}, {parsed_lon}")
                return True

        # Geocode via Nominatim
        try:
            url = "https://nominatim.openstreetmap.org/search"
            headers = {"User-Agent": "AdaptiveSmartRadarNavigator/1.0"}
            resp = requests.get(url, params={"q": query_str, "format": "json", "limit": 1}, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    item = data[0]
                    lat = float(item["lat"])
                    lon = float(item["lon"])
                    display_name = item.get("display_name", query_str).split(",")[0]
                    self.set_manual_location(lat, lon, display_name)
                    return True
        except Exception as e:
            logging.warning(f"Geocoding error for '{query_str}': {e}")

        return False

    def get_coordinates(self) -> tuple[float, float]:
        with self.lock:
            return self.latitude, self.longitude

    def get_status(self) -> dict:
        with self.lock:
            return {
                "lat": self.latitude,
                "lon": self.longitude,
                "location_name": self.location_name,
                "status_msg": self.status_msg,
                "is_locating": self.is_locating,
                "last_updated": self.last_updated,
            }
