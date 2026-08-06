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
        self.displayed_radius = float(self.steps[0])

    @property
    def current_radius(self) -> int:
        """Returns active search radius in meters."""
        return self.steps[self.step_index]

    def update(self, lerp_speed: float = 0.1):
        """Smoothly interpolates displayed radius towards active current radius."""
        target = float(self.current_radius)
        if abs(self.displayed_radius - target) > 0.5:
            self.displayed_radius += (target - self.displayed_radius) * lerp_speed
        else:
            self.displayed_radius = target

    def reset(self):
        """Resets search radius to initial baseline."""
        self.step_index = 0
        self.target_locked = False
        self.max_reached = False
        self.is_expanding = False
        self.displayed_radius = float(self.steps[0])


    def evaluate_search(self, found_count: int) -> bool:
        """
        Evaluates search results for radius expansion.
        In accept/reject mode: finding hospitals does NOT lock the search.
        Search only locks when lock_accepted() is explicitly called.
        Returns True if radius was expanded, False otherwise.
        """
        # Finding hospitals no longer locks — we only lock on acceptance.
        # If hospitals were found, don't expand yet (wait for accept/reject responses).
        if found_count > 0:
            return False

        # Expand radius if no NEW hospitals found at this step and max not reached
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

    def lock_accepted(self):
        """Called when a hospital accepts — locks the search permanently."""
        self.target_locked = True
        self.is_expanding = False

    def needs_expansion(self) -> bool:
        """Returns True if the radius can still be expanded (not at max)."""
        return self.step_index < len(self.steps) - 1

    def force_expand(self) -> bool:
        """
        Forces radius expansion to the next step.
        Used when all hospitals at current radius rejected and we need to search wider.
        Returns True if expanded, False if already at max.
        """
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
        """Formats radial meters to readable string (e.g. 50 m or 10.5 km)."""
        r = meters if meters is not None else self.current_radius
        if r >= 1000:
            return f"{r / 1000:.1f} km".replace(".0", "")
        return f"{r} m"
