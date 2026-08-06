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
        self.expanding_rings = []  # List of dicts: {radius_px, max_radius_px, alpha, speed}
        self.notifications = []    # List of dicts: {text, start_time, duration, color}
        self.sound_ping = generate_sonar_ping()

    def play_ping(self):
        """Plays sonar sound effect if Pygame audio mixer is initialized."""
        if self.sound_ping:
            try:
                self.sound_ping.play()
            except Exception:
                pass

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

        # Update notifications
        now = time.time()
        self.notifications = [n for n in self.notifications if (now - n["start_time"]) < n["duration"]]

    def draw_expanding_rings(self, surface: pygame.Surface):
        """Renders expanding radial shockwave rings."""
        for ring in self.expanding_rings:
            r = int(ring["radius_px"])
            alpha = int(ring["alpha"])
            if r > 0 and alpha > 0:
                s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 180, alpha), (r + 2, r + 2), r, 2)
                surface.blit(s, (RADAR_CENTER_X - r - 2, RADAR_CENTER_Y - r - 2))

    def draw_target_reticle(self, surface: pygame.Surface, x: int, y: int, is_locked: bool, name: str, dist_str: str):
        """Renders glowing military target reticle, lock rings, and info labels."""
        t = self.pulse_time
        base_color = COLOR_TARGET_LOCKED if is_locked else COLOR_TARGET_NORMAL

        # Pulsing target dot
        pulse_r = int(6 + math.sin(t * 8) * 2)
        pygame.draw.circle(surface, base_color, (x, y), pulse_r)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 2)

        # Connection line to radar center if locked
        if is_locked:
            s_line = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.line(s_line, (255, 60, 100, 120), (RADAR_CENTER_X, RADAR_CENTER_Y), (x, y), 1)
            surface.blit(s_line, (0, 0))

            # Tactical Lock Box & Rotating Crosshair
            box_size = 28
            rect = pygame.Rect(x - box_size // 2, y - box_size // 2, box_size, box_size)
            pygame.draw.rect(surface, COLOR_TARGET_LOCKED, rect, 1)

            # Corner brackets
            len_b = 6
            # Top-Left
            pygame.draw.line(surface, (255, 255, 255), (rect.left, rect.top), (rect.left + len_b, rect.top), 2)
            pygame.draw.line(surface, (255, 255, 255), (rect.left, rect.top), (rect.left, rect.top + len_b), 2)
            # Top-Right
            pygame.draw.line(surface, (255, 255, 255), (rect.right, rect.top), (rect.right - len_b, rect.top), 2)
            pygame.draw.line(surface, (255, 255, 255), (rect.right, rect.top), (rect.right, rect.top + len_b), 2)

        # Label Overlay
        font = pygame.font.SysFont("Consolas", 12, bold=True)
        lbl_text = f"{name} ({dist_str})"
        lbl_surf = font.render(lbl_text, True, base_color)
        surface.blit(lbl_surf, (x + 12, y - 8))

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
