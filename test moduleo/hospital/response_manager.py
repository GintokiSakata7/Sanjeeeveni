"""
Response Manager Module - Hospital Accept/Reject Tracking Engine
Manages per-hospital accept/reject state during an active expanding-radius search session.
Determines the winning hospital (shortest distance among accepted).
"""

import threading
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ResponseManager:
    """Tracks hospital accept/reject decisions during an active search."""

    # Hospital response states
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    def __init__(self):
        self.responses = {}          # hospital_id → "PENDING" | "ACCEPTED" | "REJECTED"
        self.hospital_data = {}      # hospital_id → full hospital dict (name, distance, bearing, etc.)
        self.is_search_active = False
        self.final_hospital = None   # The winning accepted hospital dict
        self.final_distance = None   # Distance in meters to winner
        self.lock = threading.Lock()

    def reset(self):
        """Clears all state for a new search session."""
        with self.lock:
            self.responses.clear()
            self.hospital_data.clear()
            self.is_search_active = True
            self.final_hospital = None
            self.final_distance = None

    def add_hospitals(self, hospitals: list):
        """
        Registers newly discovered hospitals as PENDING.
        Only adds hospitals not already tracked (avoids duplicates across radius expansions).
        Returns the list of newly added hospitals.
        """
        newly_added = []
        with self.lock:
            for h in hospitals:
                h_id = str(h.get("id", h.get("name", "")))
                if h_id not in self.responses:
                    self.responses[h_id] = self.PENDING
                    self.hospital_data[h_id] = h
                    newly_added.append(h)
        return newly_added

    def accept(self, hospital_id: str):
        """
        Marks a hospital as ACCEPTED.
        Then checks all accepted hospitals and selects the shortest distance as winner.
        Returns the winner dict if search should stop, else None.
        """
        with self.lock:
            if hospital_id in self.responses:
                self.responses[hospital_id] = self.ACCEPTED
                logging.info(f"Hospital ACCEPTED: {self.hospital_data.get(hospital_id, {}).get('name', hospital_id)}")

            return self._select_winner_locked()

    def reject(self, hospital_id: str):
        """Marks a hospital as REJECTED."""
        with self.lock:
            if hospital_id in self.responses:
                self.responses[hospital_id] = self.REJECTED
                logging.info(f"Hospital REJECTED: {self.hospital_data.get(hospital_id, {}).get('name', hospital_id)}")

    def _select_winner_locked(self):
        """
        Internal: Checks all accepted hospitals and picks the one with shortest distance.
        Must be called while holding self.lock.
        Returns the winner dict or None.
        """
        accepted = []
        for h_id, status in self.responses.items():
            if status == self.ACCEPTED:
                h_data = self.hospital_data.get(h_id)
                if h_data:
                    accepted.append(h_data)

        if accepted:
            # Pick the hospital with the shortest distance
            winner = min(accepted, key=lambda h: h.get("distance", float("inf")))
            self.final_hospital = winner
            self.final_distance = winner.get("distance", 0)
            self.is_search_active = False
            return winner

        return None

    def get_accepted(self) -> list:
        """Returns list of all hospital dicts that have been accepted."""
        with self.lock:
            result = []
            for h_id, status in self.responses.items():
                if status == self.ACCEPTED:
                    h_data = self.hospital_data.get(h_id)
                    if h_data:
                        result.append(h_data)
            return result

    def get_all_hospitals_with_status(self) -> list:
        """
        Returns list of tuples: (hospital_dict, status_string) for all tracked hospitals.
        Sorted by distance ascending.
        """
        with self.lock:
            result = []
            for h_id, status in self.responses.items():
                h_data = self.hospital_data.get(h_id)
                if h_data:
                    result.append((h_data, status))
            result.sort(key=lambda x: x[0].get("distance", float("inf")))
            return result

    def all_current_responded(self) -> bool:
        """Returns True if no hospitals are still PENDING."""
        with self.lock:
            for status in self.responses.values():
                if status == self.PENDING:
                    return False
            return True

    def has_pending(self) -> bool:
        """Returns True if there are hospitals still waiting for accept/reject."""
        with self.lock:
            return any(s == self.PENDING for s in self.responses.values())

    def get_pending_count(self) -> int:
        """Returns count of hospitals still pending."""
        with self.lock:
            return sum(1 for s in self.responses.values() if s == self.PENDING)

    def get_accepted_count(self) -> int:
        """Returns count of accepted hospitals."""
        with self.lock:
            return sum(1 for s in self.responses.values() if s == self.ACCEPTED)

    def get_rejected_count(self) -> int:
        """Returns count of rejected hospitals."""
        with self.lock:
            return sum(1 for s in self.responses.values() if s == self.REJECTED)

    def get_total_count(self) -> int:
        """Returns total number of tracked hospitals."""
        with self.lock:
            return len(self.responses)

    def is_resolved(self) -> bool:
        """Returns True if a final hospital has been selected."""
        with self.lock:
            return self.final_hospital is not None

    @staticmethod
    def format_distance(meters: float) -> str:
        """Formats distance in meters to human-readable string (e.g. '50 m', '1.2 km')."""
        if meters >= 1000:
            km = meters / 1000.0
            formatted = f"{km:.1f} km"
            return formatted.replace(".0 km", " km")
        return f"{int(round(meters))} m"
