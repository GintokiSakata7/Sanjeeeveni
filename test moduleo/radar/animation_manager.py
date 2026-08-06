"""
Adaptive Smart Radar Person Detection System
Multi-Target Visual FX & Closest YES Highlight Renderer
"""

import math
import pygame
import config
from radar import Radar
from target import Target


class RippleEffect:
    """Expanding circular shockwave ripple effect when a target is detected."""

    def __init__(self, x: float, y: float, max_radius: float = 60.0, duration: float = 1.0):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt: float) -> bool:
        self.elapsed += dt
        return self.elapsed < self.duration

    def render(self, surface: pygame.Surface):
        progress = min(1.0, self.elapsed / self.duration)
        r = int(progress * self.max_radius)
        alpha = int(255 * (1.0 - progress))

        if r > 0 and alpha > 0:
            surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
            color = (0, 255, 150, alpha)
            pygame.draw.circle(surf, color, (r + 5, r + 5), r, 2)
            surface.blit(surf, (int(self.x - r - 5), int(self.y - r - 5)))


class AnimationManager:
    """
    Renders multi-target blips, status colors (YES/NO/PENDING), selected target highlights,
    and special glowing reticles for the CLOSEST YES target.
    """

    def __init__(self):
        self.ripples: list[RippleEffect] = []

    def trigger_detection_ripple(self, x: float, y: float):
        self.ripples.append(RippleEffect(x, y, max_radius=60.0, duration=1.0))

    def update(self, dt: float):
        self.ripples = [r for r in self.ripples if r.update(dt)]

    def render_effects(self, surface: pygame.Surface):
        for ripple in self.ripples:
            ripple.render(surface)

    def render_target_blips(self, surface: pygame.Surface, radar: Radar, targets: list[Target],
                            locked_target: Target | None, font_small: pygame.font.Font, time_sec: float):
        """Renders all candidate targets with special highlighting for the closest YES target."""
        pulse = (math.sin(time_sec * 6.0) + 1.0) * 0.5

        # Find closest YES target
        yes_targets = [t for t in targets if t.status == "YES"]
        closest_yes_id = min(yes_targets, key=lambda t: t.distance_m).id if yes_targets else None

        for target in targets:
            tx, ty = radar.polar_to_cartesian(target.distance_m, target.angle_deg)
            int_x, int_y = int(tx), int(ty)

            is_closest_yes = (closest_yes_id is not None and target.id == closest_yes_id)

            # Determine Blip Color based on status & closest YES lock
            if is_closest_yes:
                color_base = config.TARGET_SHORTEST_LOCK
            elif target.status == "YES":
                color_base = config.TARGET_YES
            elif target.status == "NO":
                color_base = config.TARGET_NO
            else:
                color_base = config.TARGET_PENDING

            # 1. Selection ring if highlighted via TAB key
            if target.is_selected:
                pygame.draw.circle(surface, config.TEXT_CYAN, (int_x, int_y), 15, 1)

            # 2. Outer Glow Beacon Ring (Extra large pulse for closest YES)
            glow_radius = int(10 + pulse * 6) if is_closest_yes else (8 if target.status == "YES" else 6)
            glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
            glow_alpha = int(160 + pulse * 90) if is_closest_yes else 90

            pygame.draw.circle(glow_surf, (*color_base[:3], glow_alpha), (glow_radius + 2, glow_radius + 2), glow_radius)
            surface.blit(glow_surf, (int_x - glow_radius - 2, int_y - glow_radius - 2))

            # 3. Core Target Dot
            dot_size = 6 if is_closest_yes else 5
            pygame.draw.circle(surface, color_base, (int_x, int_y), dot_size)
            pygame.draw.circle(surface, (255, 255, 255), (int_x, int_y), 2)

            # 4. Target ID & Status Tag
            tag_label = f"★ #{target.id:02d} [CLOSEST YES] ({int(target.distance_m)}m)" if is_closest_yes else f"#{target.id:02d} [{target.status}] ({int(target.distance_m)}m)"
            tag_surf = font_small.render(tag_label, True, color_base)
            surface.blit(tag_surf, (int_x + 10, int_y - 6))

            # 5. Tactical Corner Reticle for CLOSEST YES Target
            if is_closest_yes:
                b_size = 16 + int(pulse * 4)
                gap = 6
                c_color = config.TARGET_SHORTEST_LOCK

                pygame.draw.lines(surface, c_color, False,
                                  [(int_x - b_size, int_y - gap), (int_x - b_size, int_y - b_size), (int_x - gap, int_y - b_size)], 2)
                pygame.draw.lines(surface, c_color, False,
                                  [(int_x + gap, int_y - b_size), (int_x + b_size, int_y - b_size), (int_x + b_size, int_y - gap)], 2)
                pygame.draw.lines(surface, c_color, False,
                                  [(int_x - b_size, int_y + gap), (int_x - b_size, int_y + b_size), (int_x - gap, int_y + b_size)], 2)
                pygame.draw.lines(surface, c_color, False,
                                  [(int_x + gap, int_y + b_size), (int_x + b_size, int_y + b_size), (int_x + b_size, int_y + gap)], 2)
