"""
Detector Module - Adaptive Smart Radar Navigator
Translates GPS target coordinates to radar 2D screen positions and evaluates sweep intersection.
"""

import math
from config import RADAR_CENTER_X, RADAR_CENTER_Y, RADAR_RADIUS_PX


class TargetDetector:
    """Handles radar coordinate projections and target beam-intersection logic."""

    @staticmethod
    def gps_to_radar(user_lat: float, user_lon: float, target_lat: float, target_lon: float,
                     distance_m: float, bearing_deg: float, active_radius_m: float) -> tuple[int, int, bool]:
        """
        Converts target distance and bearing relative to active search radius into screen (x, y).
        0° bearing is North (-Y), 90° is East (+X), 180° is South (+Y), 270° is West (-X).
        Returns (screen_x, screen_y, is_inside_radar_bounds).
        """
        # Distance fraction (clamp to 1.0 max for visual canvas)
        dist_ratio = min(distance_m / max(active_radius_m, 1.0), 1.0)
        pixel_distance = dist_ratio * RADAR_RADIUS_PX

        # Angle conversion (bearing 0° = North = -90° standard polar angle)
        rad = math.radians(bearing_deg)
        screen_x = int(RADAR_CENTER_X + pixel_distance * math.sin(rad))
        screen_y = int(RADAR_CENTER_Y - pixel_distance * math.cos(rad))

        is_inside = distance_m <= active_radius_m
        return screen_x, screen_y, is_inside

    @staticmethod
    def is_target_swept(target_bearing: float, current_sweep_angle: float, beam_width: float = 12.0) -> bool:
        """
        Determines if the active rotating radar sweep line (at current_sweep_angle)
        is currently passing over target_bearing within beam_width tolerance.
        """
        diff = abs((target_bearing - current_sweep_angle + 180) % 360 - 180)
        return diff <= (beam_width / 2.0)
