"""
Adaptive Smart Radar Person Detection System
Radar Sweep Beam & Fading Trail Renderer
"""

import math
import pygame
import config
from radar import Radar


class RadarSweep:
    """
    Handles continuous 360-degree rotational physics of the radar sweep beam
    and renders realistic fading phosphorescent trail sector.
    """

    def __init__(self, sweep_speed: float = config.SWEEP_SPEED_DEG_PER_FRAME):
        self.angle = 0.0  # Current beam angle in degrees (0 = North)
        self.sweep_speed = sweep_speed
        self.is_scanning = True
        self.completed_full_scan = False  # Set to True every 360° loop

    def update(self, dt_factor: float = 1.0):
        """Updates beam rotation angle."""
        if not self.is_scanning:
            return

        prev_angle = self.angle
        self.angle = (self.angle + self.sweep_speed * dt_factor) % 360.0

        # Check if completed a 360° full revolution loop
        if self.angle < prev_angle:
            self.completed_full_scan = True

    def reset_full_scan_flag(self):
        """Resets revolution flag after processing."""
        self.completed_full_scan = False

    def render(self, surface: pygame.Surface, radar: Radar, active_radius_m: float):
        """
        Renders glowing sweep beam line and multi-layer fading phosphorescent trail.
        """
        cx, cy = radar.cx, radar.cy
        active_px = radar.meters_to_pixels(active_radius_m)

        # Create temporary transparent surface for alpha trail rendering
        trail_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

        # Render trailing sector using gradient line slices
        arc_steps = 40
        arc_deg = config.SWEEP_ARC_DEGREES

        for i in range(arc_steps):
            # Angle going backwards from current beam position
            trail_deg = (self.angle - (i / arc_steps) * arc_deg) % 360.0
            rad = math.radians(trail_deg)
            
            tx = cx + active_px * math.sin(rad)
            ty = cy - active_px * math.cos(rad)

            # Alpha decays exponentially along the trail
            alpha = int(180 * (1.0 - (i / arc_steps) ** 1.5))
            if alpha > 0:
                color = (*config.RADAR_GREEN[:3], alpha)
                pygame.draw.line(trail_surface, color, (cx, cy), (tx, ty), 2)

        # Draw transparent trail layer onto main surface
        surface.blit(trail_surface, (0, 0))

        # Main Glowing Leading Beam Line
        rad_main = math.radians(self.angle)
        bx = cx + active_px * math.sin(rad_main)
        by = cy - active_px * math.cos(rad_main)

        # Multi-pass line drawing for bloom glow effect
        pygame.draw.line(surface, (0, 255, 200, 100), (cx, cy), (bx, by), 4)
        pygame.draw.line(surface, config.SWEEP_LINE_COLOR, (cx, cy), (bx, by), 2)
        pygame.draw.line(surface, (255, 255, 255), (cx, cy), (bx, by), 1)

        # Beam leading tip indicator
        pygame.draw.circle(surface, (255, 255, 255), (int(bx), int(by)), 3)
