"""
Animation & Audio Module - Adaptive Smart Radar Navigator
Renders tactical HUD animations, target reticles, expanding radius shockwaves,
notification banners, and synthesizes sonar ping sound effects via NumPy + Pygame.
"""

import math
import time
import numpy as np
import pygame
from config import (
    COLOR_TARGET_LOCKED, COLOR_TARGET_NORMAL, COLOR_TARGET_RING,
    COLOR_ACCENT_WARN, RADAR_CENTER_X, RADAR_CENTER_Y, RADAR_RADIUS_PX
)


def generate_sonar_ping(frequency: float = 950.0, duration: float = 0.12, sample_rate: int = 44100) -> pygame.mixer.Sound | None:
    """Synthesizes high-tech tactical sonar ping sound effect using NumPy."""
    try:
        import numpy as np
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Sine wave with fast exponential decay envelope
        sine = np.sin(2 * np.pi * frequency * t)
        envelope = np.exp(-15 * t)
        audio = (sine * envelope * 32767).astype(np.int16)
        stereo_audio = np.repeat(audio[:, np.newaxis], 2, axis=1)
        return pygame.sndarray.make_sound(stereo_audio)
    except Exception:
        return None



class AnimationManager:
    """Manages visual telemetry animations, expanding shockwaves, and target lock graphics."""

    def __init__(self):
        self.pulse_time = 0.0
        self.expanding_rings = []       # List of dicts: {radius_px, max_radius_px, alpha, speed}
        self.notifications = []         # List of dicts: {text, start_time, duration, color}
        self.detection_ripples = []     # List of dicts: {x, y, radius, max_radius, alpha}
        self.sound_ping = generate_sonar_ping()

    def play_ping(self):
        """Plays sonar sound effect if Pygame audio mixer is initialized."""
        if self.sound_ping:
            try:
                self.sound_ping.play()
            except Exception:
                pass

    def trigger_detection_ripple(self, x: int, y: int):
        """Spawns an expanding sonar ripple effect at target coordinates when discovered by sweep."""
        self.detection_ripples.append({
            "x": x,
            "y": y,
            "radius": 4.0,
            "max_radius": 32.0,
            "alpha": 255.0,
            "speed": 120.0
        })

    def trigger_expansion_ring(self):
        """Spawns an expanding radial shockwave when radius steps up."""
        self.expanding_rings.append({
            "radius_px": 20.0,
            "max_radius_px": float(RADAR_RADIUS_PX),
            "alpha": 255.0,
            "speed": 800.0,  # px / sec
        })

    def add_notification(self, text: str, color=COLOR_ACCENT_WARN, duration: float = 3.0):
        """Pushes a temporary HUD notification banner."""
        self.notifications.append({
            "text": text,
            "start_time": time.time(),
            "duration": duration,
            "color": color,
        })

    def update(self, dt: float):
        """Updates animation timelines by delta time `dt`."""
        self.pulse_time += dt

        # Update shockwave rings
        for ring in self.expanding_rings[:]:
            ring["radius_px"] += ring["speed"] * dt
            progress = ring["radius_px"] / ring["max_radius_px"]
            ring["alpha"] = max(0.0, 255.0 * (1.0 - progress))
            if ring["radius_px"] >= ring["max_radius_px"]:
                self.expanding_rings.remove(ring)

        # Update detection ripples
        for rip in self.detection_ripples[:]:
            rip["radius"] += rip["speed"] * dt
            prog = rip["radius"] / rip["max_radius"]
            rip["alpha"] = max(0.0, 255.0 * (1.0 - prog))
            if rip["radius"] >= rip["max_radius"]:
                self.detection_ripples.remove(rip)

        # Update notifications
        now = time.time()
        self.notifications = [n for n in self.notifications if (now - n["start_time"]) < n["duration"]]

    def draw_expanding_rings(self, surface: pygame.Surface):
        """Renders expanding radial shockwave rings and target ripples."""
        for ring in self.expanding_rings:
            r = int(ring["radius_px"])
            alpha = int(ring["alpha"])
            if r > 0 and alpha > 0:
                s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 180, alpha), (r + 2, r + 2), r, 2)
                surface.blit(s, (RADAR_CENTER_X - r - 2, RADAR_CENTER_Y - r - 2))

        # Render detection ripples at target blip coordinates
        for rip in self.detection_ripples:
            rx, ry = int(rip["x"]), int(rip["y"])
            rr = int(rip["radius"])
            ralpha = int(rip["alpha"])
            if rr > 0 and ralpha > 0:
                s_rip = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s_rip, (0, 255, 200, ralpha), (rr + 2, rr + 2), rr, 2)
                surface.blit(s_rip, (rx - rr - 2, ry - rr - 2))

    def draw_target_reticle(self, surface: pygame.Surface, x: int, y: int, is_locked: bool, name: str, dist_str: str, status: str = "PENDING"):
        """
        Renders authentic Hospital Badge Icon on radar screen.
        Status colors:
          - PENDING: Amber/Yellow (255, 190, 0)
          - ACCEPTED: Neon Green (0, 255, 140)
          - REJECTED: Muted Gray (120, 130, 140)
          - LOCKED/WINNER: Crimson Red (255, 60, 100) with tracking vector line
        """
        t = self.pulse_time

        if is_locked:
            badge_color = COLOR_TARGET_LOCKED
            status_tag = "WINNER (ACCEPTED)"
        elif status == "ACCEPTED":
            badge_color = (0, 255, 140)
            status_tag = "ACCEPTED"
        elif status == "REJECTED":
            badge_color = (120, 130, 140)
            status_tag = "REJECTED"
        else:
            badge_color = (255, 190, 0)
            status_tag = "PENDING"

        # Connection tracking line to center if locked winner
        if is_locked:
            s_line = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.line(s_line, (255, 60, 100, 140), (RADAR_CENTER_X, RADAR_CENTER_Y), (x, y), 2)
            surface.blit(s_line, (0, 0))

        # Pulsing outer aura ring
        pulse_r = int(14 + math.sin(t * 6) * 3)
        if status != "REJECTED":
            s_pulse = pygame.Surface((pulse_r * 2 + 4, pulse_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s_pulse, (*badge_color[:3], 70), (pulse_r + 2, pulse_r + 2), pulse_r)
            surface.blit(s_pulse, (x - pulse_r - 2, y - pulse_r - 2))

        # 1. Hospital Icon Badge Box (Rounded Rectangle with Cross)
        badge_w, badge_h = 20, 20
        badge_rect = pygame.Rect(x - badge_w // 2, y - badge_h // 2, badge_w, badge_h)
        pygame.draw.rect(surface, (12, 24, 30), badge_rect, border_radius=4)
        pygame.draw.rect(surface, badge_color, badge_rect, 2, border_radius=4)

        # White Medical Cross (+) inside badge
        cw, ch = 10, 3
        # Horizontal
        pygame.draw.rect(surface, (255, 255, 255), (x - cw // 2, y - ch // 2, cw, ch))
        # Vertical
        pygame.draw.rect(surface, (255, 255, 255), (x - ch // 2, y - cw // 2, ch, cw))

        # 2. Tactical Reticle Brackets if Locked Winner
        if is_locked:
            b_size = 30
            b_rect = pygame.Rect(x - b_size // 2, y - b_size // 2, b_size, b_size)
            pygame.draw.rect(surface, COLOR_TARGET_LOCKED, b_rect, 1)

            # Corner bracket ticks
            lb = 6
            pygame.draw.line(surface, (255, 255, 255), (b_rect.left, b_rect.top), (b_rect.left + lb, b_rect.top), 2)
            pygame.draw.line(surface, (255, 255, 255), (b_rect.left, b_rect.top), (b_rect.left, b_rect.top + lb), 2)
            pygame.draw.line(surface, (255, 255, 255), (b_rect.right, b_rect.top), (b_rect.right - lb, b_rect.top), 2)
            pygame.draw.line(surface, (255, 255, 255), (b_rect.right, b_rect.top), (b_rect.right, b_rect.top + lb), 2)

        # 3. Text Overlay Label
        font_lbl = pygame.font.SysFont("Consolas", 11, bold=True)
        lbl_text = f"🏥 {name} ({dist_str})"
        lbl_surf = font_lbl.render(lbl_text, True, badge_color)
        surface.blit(lbl_surf, (x + 14, y - 8))

    def draw_notifications(self, surface: pygame.Surface):
        """Renders HUD notification banners on top center of screen."""
        if not self.notifications:
            return

        font = pygame.font.SysFont("Consolas", 14, bold=True)
        now = time.time()
        start_y = 60

        for n in self.notifications:
            elapsed = now - n["start_time"]
            fade = min(1.0, (n["duration"] - elapsed) / 0.5) if elapsed > (n["duration"] - 0.5) else 1.0
            alpha = int(255 * max(0.0, fade))

            txt_surf = font.render(n["text"], True, n["color"])
            padding = 10
            bg_rect = pygame.Rect(
                RADAR_CENTER_X - txt_surf.get_width() // 2 - padding,
                start_y,
                txt_surf.get_width() + padding * 2,
                txt_surf.get_height() + padding
            )

            banner_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            banner_surf.fill((10, 20, 26, int(220 * (alpha / 255.0))))
            pygame.draw.rect(banner_surf, (n["color"][0], n["color"][1], n["color"][2], alpha), banner_surf.get_rect(), 1)

            surface.blit(banner_surf, (bg_rect.x, bg_rect.y))
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, (bg_rect.x + padding, bg_rect.y + padding // 2))

            start_y += bg_rect.height + 6
