"""
Adaptive Smart Radar Person Detection System
Adaptive Search Radius Manager
"""

import config


class RadiusManager:
    """
    Controls the adaptive expansion of the radar scanning radius.
    Starts at 50m, expands by 50m after each full scan pass without target detection,
    up to configured maximum (500m). Smoothly interpolates active UI radius ring.
    """

    def __init__(self, initial_radius: float = config.INITIAL_RADIUS_METERS,
                 step: float = config.RADIUS_STEP_METERS,
                 max_radius: float = config.MAX_RADIUS_METERS):
        self.initial_radius = initial_radius
        self.step = step
        self.max_radius = max_radius
        
        self.current_radius = initial_radius
        self.target_radius = initial_radius
        self.displayed_radius = initial_radius  # Interpolated for smooth UI animation
        
        self.expansion_count = 0
        self.is_max_reached = False
        self.auto_expand = True  # Automatically expand after full sweeps if unlocked

    def expand(self) -> bool:
        """
        Increases the search radius by step size (e.g. +50m) if below max_radius.
        Returns True if expanded, False if already at max.
        """
        if not self.auto_expand:
            return False

        if self.current_radius < self.max_radius:
            self.current_radius += self.step
            if self.current_radius > self.max_radius:
                self.current_radius = self.max_radius
                self.is_max_reached = True
            
            self.target_radius = self.current_radius
            self.expansion_count += 1
            return True
        else:
            self.is_max_reached = True
            return False

    def update(self, lerp_speed: float = 0.1):
        """Smoothly animates displayed radius towards current active radius."""
        if abs(self.displayed_radius - self.current_radius) > 0.1:
            self.displayed_radius += (self.current_radius - self.displayed_radius) * lerp_speed
        else:
            self.displayed_radius = self.current_radius

    def is_in_range(self, distance_m: float) -> bool:
        """Checks if a given distance in meters is within the active search radius."""
        return distance_m <= self.current_radius

    def reset(self):
        """Resets search radius back to initial 50m."""
        self.current_radius = self.initial_radius
        self.target_radius = self.initial_radius
        self.displayed_radius = self.initial_radius
        self.expansion_count = 0
        self.is_max_reached = False
        self.auto_expand = True
