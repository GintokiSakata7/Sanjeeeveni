"""
Adaptive Smart Radar Person Detection System
Radar Scope Model & Math Utilities
"""

import math
import numpy as np
import pygame
import config


class Radar:
    """
    Manages radar coordinate transformations (Polar <-> Cartesian),
    scale math (Meters <-> Pixels), and renders the military radar grid background.
    """

    def __init__(self, center_x=config.RADAR_CENTER_X, center_y=config.RADAR_CENTER_Y,
                 pixel_radius=config.RADAR_PIXEL_RADIUS, max_meters=config.MAX_RADIUS_METERS):
        self.cx = center_x
        self.cy = center_y
        self.pixel_radius = pixel_radius
        self.max_meters = max_meters
        self.scale_px_per_m = pixel_radius / max_meters

    def meters_to_pixels(self, meters: float) -> float:
        """Converts distance in meters to screen pixel radius."""
        return meters * self.scale_px_per_m

    def pixels_to_meters(self, pixels: float) -> float:
        """Converts screen pixel radius to meters."""
        return pixels / self.scale_px_per_m

    def polar_to_cartesian(self, distance_m: float, angle_deg: float) -> tuple[float, float]:
        """
        Converts Polar Coordinates (distance in meters, angle in degrees 0-360, 0=North clockwise)
        to Screen Cartesian Coordinates (x, y).
        """
        r_px = self.meters_to_pixels(distance_m)
        rad = math.radians(angle_deg % 360)
        x = self.cx + r_px * math.sin(rad)
        y = self.cy - r_px * math.cos(rad)
        return x, y

    def cartesian_to_polar(self, x: float, y: float) -> tuple[float, float]:
        """
        Converts Screen Cartesian Coordinates (x, y) to Polar (distance_m, angle_deg).
        """
        dx = x - self.cx
        dy = y - self.cy
        r_px = math.hypot(dx, dy)
        distance_m = self.pixels_to_meters(r_px)
        
        rad = math.atan2(dx, -dy)
        angle_deg = math.degrees(rad) % 360.0
        return distance_m, angle_deg

    def render_grid(self, surface: pygame.Surface, current_active_radius_m: float, font_small: pygame.font.Font):
        """
        Renders futuristic military radar background grid, degree markings, concentric distance rings,
        and compass cardinal indicators (N, E, S, W).
        """
        # Outer Radar Scope Boundary Ring
        pygame.draw.circle(surface, config.RADAR_DARK_GREEN, (self.cx, self.cy), self.pixel_radius, 2)
        pygame.draw.circle(surface, config.RADAR_GREEN, (self.cx, self.cy), self.pixel_radius + 4, 1)

        # Concentric Distance Rings (every 50 meters up to max range)
        num_rings = int(self.max_meters / config.RADIUS_STEP_METERS)
        for i in range(1, num_rings + 1):
            ring_m = i * config.RADIUS_STEP_METERS
            ring_px = int(self.meters_to_pixels(ring_m))
            
            # Subtle green ring for grid
            pygame.draw.circle(surface, config.RADAR_GRID_SUBTLE, (self.cx, self.cy), ring_px, 1)
            
            # Draw distance label (e.g. "100m") on North axis
            lbl = font_small.render(f"{int(ring_m)}m", True, config.TEXT_MUTED)
            surface.blit(lbl, (self.cx + 5, self.cy - ring_px - 8))

        # Highlight Active Search Radius Ring
        active_px = int(self.meters_to_pixels(current_active_radius_m))
        if active_px <= self.pixel_radius:
            pygame.draw.circle(surface, config.ACTIVE_RADIUS_RING_COLOR, (self.cx, self.cy), active_px, 2)

        # Draw Major & Minor Crosshair Axis Lines
        pygame.draw.line(surface, config.RADAR_DARK_GREEN, 
                         (self.cx - self.pixel_radius - 10, self.cy), 
                         (self.cx + self.pixel_radius + 10, self.cy), 1)
        pygame.draw.line(surface, config.RADAR_DARK_GREEN, 
                         (self.cx, self.cy - self.pixel_radius - 10), 
                         (self.cx, self.cy + self.pixel_radius + 10), 1)

        # Draw Degree Ticks and Angle Lines (every 30 degrees)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            # Line endpoints
            x1 = self.cx + (self.pixel_radius - 8) * sin_a
            y1 = self.cy - (self.pixel_radius - 8) * cos_a
            x2 = self.cx + (self.pixel_radius + 6) * sin_a
            y2 = self.cy - (self.pixel_radius + 6) * cos_a
            
            pygame.draw.line(surface, config.RADAR_DARK_GREEN, (x1, y1), (x2, y2), 1)

            # Radial dashed line to center for major cardinal angles (0, 90, 180, 270)
            if angle % 90 == 0:
                pygame.draw.line(surface, config.RADAR_DARK_GREEN, (self.cx, self.cy), (x1, y1), 1)

            # Degree Text Labels around outer perimeter
            lx = self.cx + (self.pixel_radius + 20) * sin_a
            ly = self.cy - (self.pixel_radius + 20) * cos_a
            deg_str = f"{angle}°"
            deg_txt = font_small.render(deg_str, True, config.TEXT_PRIMARY)
            deg_rect = deg_txt.get_rect(center=(int(lx), int(ly)))
            surface.blit(deg_txt, deg_rect)

        # Cardinal Indicators (N, E, S, W)
        cardinals = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
        for label, deg in cardinals:
            rad = math.radians(deg)
            cx_pos = self.cx + (self.pixel_radius - 22) * math.sin(rad)
            cy_pos = self.cy - (self.pixel_radius - 22) * math.cos(rad)
            c_txt = font_small.render(label, True, config.TEXT_CYAN)
            c_rect = c_txt.get_rect(center=(int(cx_pos), int(cy_pos)))
            surface.blit(c_txt, c_rect)

        # Center Radar Hub Dot
        pygame.draw.circle(surface, config.RADAR_GREEN, (self.cx, self.cy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (self.cx, self.cy), 2)
