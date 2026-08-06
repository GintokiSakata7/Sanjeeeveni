"""
Radius Manager Module - Adaptive Smart Radar Navigator
Manages step-wise adaptive radial expansion (500m -> 1km -> 2km -> 5km -> 10km -> 20km -> 50km).
Controls search radius state, target lock status, and expansion notifications.
"""

from config import RADIUS_STEPS


class RadiusManager:
    """Manages adaptive radial stepping and search progression states."""

    def __init__(self):
        self.steps = RADIUS_STEPS
        self.step_index = 0
        self.target_locked = False
        self.max_reached = False
        self.is_expanding = False

    @property
    def current_radius(self) -> int:
        """Returns active search radius in meters."""
        return self.steps[self.step_index]

    def reset(self):
        """Resets search radius to initial 500m baseline."""
        self.step_index = 0
        self.target_locked = False
        self.max_reached = False
        self.is_expanding = False

    def evaluate_search(self, found_count: int) -> bool:
        """
        Evaluates search results:
        If found_count > 0: Locks target search and stops expansion.
        If found_count == 0: Advances to next larger radius step.
        Returns True if radius was expanded, False otherwise.
        """
        if found_count > 0:
            self.target_locked = True
            self.is_expanding = False
            return False

        # Expand radius if targets not found and max not reached
        if self.step_index < len(self.steps) - 1:
            self.step_index += 1
            self.is_expanding = True
            if self.step_index == len(self.steps) - 1:
                self.max_reached = True
            return True
        else:
            self.max_reached = True
            self.is_expanding = False
            return False

    def format_radius(self, meters: int = None) -> str:
        """Formats radial meters to readable string (e.g. 500m or 10.5 km)."""
        r = meters if meters is not None else self.current_radius
        if r >= 1000:
            return f"{r / 1000:.1f} km".replace(".0", "")
        return f"{r} m"
