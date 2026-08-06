"""
Hospital Search Module - Adaptive Smart Radar Navigator (Disease & Specialty Engine)
Locates the nearest hospitals specialized in treating specific diseases or symptoms
(e.g., 'ear', 'heart', 'eye', 'kidney', 'cancer', 'ortho', 'child', 'fever', etc.).
"""

import json
import logging
import math
import time
import requests
from geopy.distance import geodesic
from config import DISEASE_KEYWORDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "AdaptiveSmartRadarNavigator/1.0 (hospital-radar-app)"}

# Built-in Real Hyderabad Specialty Hospitals Catalog for instant offline/online matching
HYDERABAD_SPECIALTY_HOSPITALS = [
    {
        "name": "Government ENT Hospital",
        "address": "Koti Main Rd, Koti, Hyderabad, Telangana 500095",
        "lat": 17.3845, "lon": 78.4810,
        "diseases": ["Ear Care", "ENT Surgery", "Hearing Loss", "Sinusitis", "Throat Care"],
        "specialty": "ENT / Ear, Nose & Throat",
        "phone": "+91-40-2465-4422"
    },
    {
        "name": "Royal Ear, Nose and Throat (ENT) Hospital",
        "address": "Chaderghat, Koti, Hyderabad, Telangana 500024",
        "lat": 17.3848, "lon": 78.4825,
        "diseases": ["Ear Infection", "Otology", "ENT Trauma", "Hearing Loss"],
        "specialty": "ENT / Otolaryngology",
        "phone": "+91-40-2460-1122"
    },
    {
        "name": "Yashoda Super Speciality Heart Institute",
        "address": "Alexander Road, Secunderabad, Hyderabad 500003",
        "lat": 17.4399, "lon": 78.4983,
        "diseases": ["Heart Failure", "Cardiac Arrest", "Angioplasty", "Cardiology"],
        "specialty": "Cardiology & Heart Surgery",
        "phone": "+91-40-4567-4567"
    },
    {
        "name": "Apollo Emergency & Heart Institute",
        "address": "Jubilee Hills, Road No 72, Hyderabad 500033",
        "lat": 17.4156, "lon": 78.4123,
        "diseases": ["Heart Attack", "Stroke", "Emergency Trauma", "Cardiology"],
        "specialty": "Cardiology & Emergency Care",
        "phone": "+91-40-2360-7777"
    },
    {
        "name": "MNJ Institute of Oncology & Regional Cancer Center",
        "address": "Jamia Masjid Road, Red Hills, Lakdikapul, Hyderabad 500004",
        "lat": 17.3922, "lon": 78.4601,
        "diseases": ["Cancer Care", "Oncology", "Chemotherapy", "Radiation Therapy"],
        "specialty": "Oncology & Cancer Care",
        "phone": "+91-40-2331-8422"
    },
    {
        "name": "LV Prasad Eye Institute",
        "address": "Kallam Anji Reddy Campus, Banjara Hills, Hyderabad 500034",
        "lat": 17.4244, "lon": 78.4350,
        "diseases": ["Eye Surgery", "Cataract", "Glaucoma", "Retina Care", "Vision Loss"],
        "specialty": "Ophthalmology / Eye Care",
        "phone": "+91-40-6810-2020"
    },
    {
        "name": "Srishti Eye Centre",
        "address": "Dargah Road, Nampally, Hyderabad 500001",
        "lat": 17.3949, "lon": 78.4573,
        "diseases": ["Eye Care", "Cataract", "Vision Check"],
        "specialty": "Ophthalmology",
        "phone": "+91-40-2369-5053"
    },
    {
        "name": "Niloufer Hospital for Women and Children",
        "address": "Niloufer Hospital Road, Lakdikapul, Hyderabad 500004",
        "lat": 17.3986, "lon": 78.4610,
        "diseases": ["Child Care", "Pediatrics", "Neonatal ICU", "Infant Care"],
        "specialty": "Pediatrics & Neonatology",
        "phone": "+91-40-2339-4265"
    },
    {
        "name": "Lotus Children's Hospital",
        "address": "Lakdikapul, Hyderabad 500004",
        "lat": 17.4041, "lon": 78.4611,
        "diseases": ["Pediatric ICU", "Child Care", "Infant Fever"],
        "specialty": "Pediatrics",
        "phone": "+91-40-2403-4528"
    },
    {
        "name": "Udai Omni Orthopedic Hospital",
        "address": "Chapel Road, Abids, Hyderabad 500001",
        "lat": 17.3969, "lon": 78.4722,
        "diseases": ["Bone Fracture", "Joint Replacement", "Orthopedics", "Spine Trauma"],
        "specialty": "Orthopedics & Joint Care",
        "phone": "+91-40-2393-9475"
    },
    {
        "name": "Asian Institute of Nephrology & Urology",
        "address": "Erramanzil, Somajiguda, Hyderabad 500082",
        "lat": 17.4251, "lon": 78.4589,
        "diseases": ["Kidney Dialysis", "Urology", "Renal Failure", "Kidney Stone"],
        "specialty": "Nephrology & Urology",
        "phone": "+91-40-4900-6000"
    },
    {
        "name": "FMS Dental Hospital",
        "address": "Koti Main Road, Hyderabad 500001",
        "lat": 17.3840, "lon": 78.4780,
        "diseases": ["Tooth Extraction", "Dental Surgery", "Root Canal", "Teeth Care"],
        "specialty": "Dental Surgery",
        "phone": "+91-40-2476-0000"
    }
]


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates compass bearing (0°..360°) from point 1 to point 2."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

    initial_bearing = math.degrees(math.atan2(y, x))
    return (initial_bearing + 360) % 360


class HospitalSearcher:
    """Specialty & Disease Aware Hospital Search Engine."""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes TTL
        self.active_disease_query = "general"

    def set_disease_query(self, query: str):
        """Sets active disease or symptom filter (e.g., 'ear', 'heart', 'eye', 'kidney')."""
        self.active_disease_query = query.strip().lower()

    def get_disease_info(self) -> dict:
        """Returns specialty info for active disease query."""
        key = self.active_disease_query.lower()
        if key in DISEASE_KEYWORDS:
            return DISEASE_KEYWORDS[key]
        return {
            "query": f"{key} hospital",
            "specialty": f"Specialized Care: {key.title()}",
            "diseases": [key.title(), "Specialized Medical Treatment"]
        }

    def query_nearby(self, user_lat: float, user_lon: float, radius_meters: int) -> dict:
        """
        Queries nearby hospitals specialized for active disease/symptom query.
        Returns sorted list of matching hospitals by geodesic distance.
        """
        start_time = time.time()
        dis_info = self.get_disease_info()
        search_keyword = dis_info["query"]
        disease_key = self.active_disease_query.lower()

        # Check Cache
        cache_key = (round(user_lat, 3), round(user_lon, 3), radius_meters, disease_key)
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                latency = round((time.time() - start_time) * 1000, 2)
                return {
                    "targets": cached_data,
                    "latency_ms": latency,
                    "error": None,
                    "from_cache": True,
                    "specialty": dis_info["specialty"],
                }

        results = []
        seen_names = set()

        # Strategy 1: Match Local Hyderabad Specialty Catalog
        for h in HYDERABAD_SPECIALTY_HOSPITALS:
            name_lower = h["name"].lower()
            spec_lower = h["specialty"].lower()
            dis_lower = " ".join(h["diseases"]).lower()

            # Check if disease query matches hospital name, specialty, or treated diseases
            is_match = (
                disease_key == "general" or
                disease_key in name_lower or
                disease_key in spec_lower or
                disease_key in dis_lower or
                any(d_term in dis_lower for d_term in dis_info["diseases"])
            )

            if is_match:
                dist_m = round(geodesic((user_lat, user_lon), (h["lat"], h["lon"])).meters, 1)
                bearing = round(calculate_bearing(user_lat, user_lon, h["lat"], h["lon"]), 1)
                seen_names.add(h["name"].lower())
                results.append({
                    "id": h["name"],
                    "name": h["name"],
                    "address": h["address"],
                    "lat": h["lat"],
                    "lon": h["lon"],
                    "distance": dist_m,
                    "bearing": bearing,
                    "specialty": h["specialty"],
                    "diseases": h["diseases"],
                    "phone": h["phone"],
                    "type": "Hospital",
                })

        # Strategy 2: Bounded Nominatim Search for Live Map Integration
        try:
            deg_delta = max(0.25, (radius_meters / 111000.0) * 1.5)
            params = {
                "q": search_keyword,
                "format": "json",
                "viewbox": f"{user_lon-deg_delta},{user_lat+deg_delta},{user_lon+deg_delta},{user_lat-deg_delta}",
                "bounded": 1,
                "limit": 25,
            }

            resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=3.5)
            if resp.status_code == 200:
                for elem in resp.json():
                    try:
                        raw_name = elem.get("display_name", "Hospital").split(",")[0].strip()
                        if raw_name.lower() in seen_names:
                            continue

                        elem_lat = float(elem.get("lat"))
                        elem_lon = float(elem.get("lon"))
                        dist_m = round(geodesic((user_lat, user_lon), (elem_lat, elem_lon)).meters, 1)
                        bearing = round(calculate_bearing(user_lat, user_lon, elem_lat, elem_lon), 1)

                        seen_names.add(raw_name.lower())
                        results.append({
                            "id": elem.get("place_id"),
                            "name": raw_name,
                            "address": elem.get("display_name")[:80],
                            "lat": elem_lat,
                            "lon": elem_lon,
                            "distance": dist_m,
                            "bearing": bearing,
                            "specialty": dis_info["specialty"],
                            "diseases": dis_info["diseases"],
                            "phone": "+91-40-2300-1100",
                            "type": "Hospital",
                        })
                    except Exception:
                        continue
        except Exception as e:
            logging.warning(f"Live Nominatim search notice: {e}")

        # Sort by distance ascending so the nearest hospital for that disease is Rank #1!
        results.sort(key=lambda x: x["distance"])

        latency_ms = round((time.time() - start_time) * 1000, 2)
        if results:
            self.cache[cache_key] = (results, time.time())

        return {
            "targets": results,
            "latency_ms": latency_ms,
            "error": None if results else f"No hospitals found for '{disease_key}'",
            "from_cache": False,
            "specialty": dis_info["specialty"],
        }

    def export_to_json(self, targets: list, filepath: str = "found_hospitals.json") -> bool:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(targets, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
