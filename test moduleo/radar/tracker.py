"""
Adaptive Smart Radar Person Detection System
Multi-Target Tracker & Closest YES Selection Engine
"""

import math
import pygame
import config
from target import Target
from radar import Radar


class Tracker:
    """
    Manages target tracking across multiple candidate points.
    Prioritizes and highlights the CLOSEST target marked 'YES' (shortest distance).
    """

    def __init__(self, auto_track: bool = True):
        self.is_locked = False
        self.auto_track = auto_track
        self.locked_target: Target | None = None
        self.all_candidates: list[Target] = []
        self.lock_timestamp = 0.0

    def update_tracking(self, active_radius_m: float, targets: list[Target], timestamp: float):
        """
        Evaluates all targets marked 'YES' inside active search radius and locks onto
        the CLOSEST target (shortest distance to radar hub).
        """
        valid_targets = [t for t in targets if t.distance_m <= active_radius_m and t.status != "NO"]
        self.all_candidates = valid_targets

        # Filter all YES-confirmed targets
        yes_targets = [t for t in targets if t.status == "YES"]

        if yes_targets:
            # Highlight and lock onto the CLOSEST YES target
            closest_yes = min(yes_targets, key=lambda t: t.distance_m)
            self.locked_target = closest_yes
            self.is_locked = True
        elif valid_targets:
            # Fallback to closest pending target
            closest_pending = min(valid_targets, key=lambda t: t.distance_m)
            self.locked_target = closest_pending
            self.is_locked = False
        else:
            self.locked_target = None
            self.is_locked = False

    def toggle_auto_track(self) -> bool:
        self.auto_track = not self.auto_track
        return self.auto_track

    def render_tracking(self, surface: pygame.Surface, radar: Radar, font_bold: pygame.font.Font, time_sec: float):
        """
        Renders laser vector ray to closest YES target and secondary rays to other candidate points.
        """
        cx, cy = radar.cx, radar.cy

        # 1. Render Secondary Lines to other points
        for t in self.all_candidates:
            if self.locked_target and t.id == self.locked_target.id:
                continue

            tx, ty = radar.polar_to_cartesian(t.distance_m, t.angle_deg)
            line_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            color = (0, 255, 102, 80) if t.status == "YES" else (0, 229, 255, 60)
            pygame.draw.line(line_surf, color, (cx, cy), (int(tx), int(ty)), 1)
            surface.blit(line_surf, (0, 0))

        # 2. Render Primary Laser Tracking Ray to CLOSEST YES target
        if self.locked_target:
            t = self.locked_target
            tx, ty = radar.polar_to_cartesian(t.distance_m, t.angle_deg)

            alpha = int(180 + 75 * math.sin(time_sec * 8.0))
            is_yes = (t.status == "YES")
            track_color = (255, 40, 60, alpha) if is_yes else (255, 200, 0, alpha)

            line_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            pygame.draw.line(line_surf, track_color, (cx, cy), (int(tx), int(ty)), 2)
            surface.blit(line_surf, (0, 0))

            # HUD Label
            if int(time_sec * 4.0) % 2 == 0:
                lbl_str = f"★ CLOSEST YES LOCK #{t.id:02d} ({t.distance_m:.1f}m)" if is_yes else f"CANDIDATE #{t.id:02d} ({t.distance_m:.1f}m)"
                lbl_color = config.TARGET_SHORTEST_LOCK if is_yes else config.TARGET_PENDING

                txt = font_bold.render(lbl_str, True, lbl_color)
                txt_rect = txt.get_rect(center=(int(tx), int(ty) - 26))

                bg_rect = txt_rect.inflate(12, 6)
                pygame.draw.rect(surface, (15, 0, 0, 210), bg_rect, border_radius=4)
                pygame.draw.rect(surface, lbl_color, bg_rect, 1, border_radius=4)
                surface.blit(txt, txt_rect)
