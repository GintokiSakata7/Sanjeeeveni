"""
Radar Canvas Module - Adaptive Smart Radar Navigator
Renders concentric radar rings, degree markings, crosshair grids, rotating sweep beam,
mini direction compass, and canvas telemetry overlays.
"""

import math
import pygame
from config import (
    RADAR_CENTER_X, RADAR_CENTER_Y, RADAR_RADIUS_PX,
    COLOR_BG, COLOR_RADAR_GRID, COLOR_RADAR_RING, COLOR_RADAR_SWEEP,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_ACCENT_WARN, COLOR_ACCENT_ALERT,
    COLOR_TARGET_LOCKED
)


class RadarCanvas:
    """Renders the 360-degree tactical radar screen graphics and rotating sweep beam."""

    def __init__(self):
        self.sweep_angle = 0.0      # Degrees (0°..360°)
        self.sweep_speed = 120.0    # Degrees per second (1 full rotation every 3 seconds)
        self.completed_full_scan = False
        self.font_degree = pygame.font.SysFont("Consolas", 11, bold=True)
        self.font_header = pygame.font.SysFont("Consolas", 14, bold=True)

    def update_sweep(self, dt: float):
        """Advances rotating sweep angle by delta time `dt`."""
        prev_angle = self.sweep_angle
        self.sweep_angle = (self.sweep_angle + self.sweep_speed * dt) % 360.0
        if self.sweep_angle < prev_angle:
            self.completed_full_scan = True

    def reset_full_scan_flag(self):
        self.completed_full_scan = False

    def draw(self, surface: pygame.Surface, active_radius_str: str, target_count: int, is_locked: bool, status_msg: str, displayed_radius: float = None, max_radius: float = None):
        """Draws complete radar background, concentric circles, active range ring, sweep beam, and compass."""
        cx, cy, r = RADAR_CENTER_X, RADAR_CENTER_Y, RADAR_RADIUS_PX

        # 1. Canvas Outer Boundary Circle & Dark Fill
        pygame.draw.circle(surface, (10, 18, 22), (cx, cy), r)
        pygame.draw.circle(surface, COLOR_RADAR_RING, (cx, cy), r, 2)

        # 2. Concentric Radial Circles (25%, 50%, 75%)
        for ratio in [0.25, 0.50, 0.75]:
            sub_r = int(r * ratio)
            pygame.draw.circle(surface, COLOR_RADAR_GRID, (cx, cy), sub_r, 1)

        # Active Search Radius Ring (Dynamic Cyan Ring matching displayed_radius)
        if displayed_radius is not None and max_radius is not None and max_radius > 0:
            active_ratio = min(displayed_radius / max_radius, 1.0)
            active_px = int(r * active_ratio)
            if active_px > 5:
                # Cyan glowing search ring
                s_ring = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(s_ring, (0, 229, 255, 180), (r + 5, r + 5), active_px, 2)
                surface.blit(s_ring, (cx - r - 5, cy - r - 5))

        # 3. Crosshair Grid Lines (N-S, E-W)

        pygame.draw.line(surface, COLOR_RADAR_GRID, (cx - r, cy), (cx + r, cy), 1)
        pygame.draw.line(surface, COLOR_RADAR_GRID, (cx, cy - r), (cx, cy + r), 1)

        # Diagonal Grid Lines (45° and 135°)
        diag_offset = int(r * 0.7071)
        pygame.draw.line(surface, (0, 45, 35), (cx - diag_offset, cy - diag_offset), (cx + diag_offset, cy + diag_offset), 1)
        pygame.draw.line(surface, (0, 45, 35), (cx - diag_offset, cy + diag_offset), (cx + diag_offset, cy - diag_offset), 1)

        # 4. Cardinal & Degree Markings
        cardinals = [(0, "N (0°)"), (90, "E (90°)"), (180, "S (180°)"), (270, "W (270°)")]
        for deg, label in cardinals:
            rad = math.radians(deg)
            tx = cx + (r + 16) * math.sin(rad)
            ty = cy - (r + 16) * math.cos(rad)
            txt_surf = self.font_degree.render(label, True, COLOR_TEXT_SECONDARY)
            surface.blit(txt_surf, (tx - txt_surf.get_width() // 2, ty - txt_surf.get_height() // 2))

        # Additional 30-degree tick marks
        for deg in range(0, 360, 30):
            if deg % 90 == 0:
                continue
            rad = math.radians(deg)
            x1 = cx + (r - 6) * math.sin(rad)
            y1 = cy - (r - 6) * math.cos(rad)
            x2 = cx + r * math.sin(rad)
            y2 = cy - r * math.cos(rad)
            pygame.draw.line(surface, COLOR_RADAR_RING, (x1, y1), (x2, y2), 1)

        # 5. Rotating 360° Sweep Arc Tail & Sweep Beam Line
        self._draw_sweep_beam(surface, cx, cy, r)

        # 6. Center Origin Pulse Marker
        pygame.draw.circle(surface, COLOR_RADAR_SWEEP, (cx, cy), 4)

        # 7. Radar Canvas Top Status Banner
        status_color = COLOR_TARGET_LOCKED if is_locked else (COLOR_ACCENT_WARN if target_count == 0 else COLOR_TEXT_PRIMARY)
        hdr_text = f"RANGE: {active_radius_str} | TARGETS: {target_count} | STATUS: {status_msg.upper()}"
        hdr_surf = self.font_header.render(hdr_text, True, status_color)
        surface.blit(hdr_surf, (cx - hdr_surf.get_width() // 2, cy - r - 42))

        # 8. Mini Directional Compass (Bottom-Left of Canvas)
        self._draw_mini_compass(surface, cx - r + 40, cy + r - 40)

    def _draw_sweep_beam(self, surface: pygame.Surface, cx: int, cy: int, r: int):
        """Renders the primary rotating sweep line and transparent fading arc tail."""
        sweep_rad = math.radians(self.sweep_angle)
        sx = cx + r * math.sin(sweep_rad)
        sy = cy - r * math.cos(sweep_rad)

        # Draw fading arc sector tail (last 30 degrees)
        arc_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        center_arc = (r + 5, r + 5)
        num_segments = 25
        arc_angle_span = 35.0  # Degrees

        points = [center_arc]
        for i in range(num_segments + 1):
            angle_deg = self.sweep_angle - (arc_angle_span * (i / num_segments))
            rad = math.radians(angle_deg)
            px = center_arc[0] + r * math.sin(rad)
            py = center_arc[1] - r * math.cos(rad)
            points.append((px, py))

        if len(points) > 2:
            pygame.draw.polygon(arc_surf, (0, 255, 140, 35), points)
            surface.blit(arc_surf, (cx - r - 5, cy - r - 5))

        # Main glowing sweep line
        pygame.draw.line(surface, COLOR_RADAR_SWEEP, (cx, cy), (sx, sy), 2)

    def _draw_mini_compass(self, surface: pygame.Surface, x: int, y: int):
        """Draws a mini compass widget displaying North orientation."""
        r_comp = 22
        pygame.draw.circle(surface, (15, 30, 35), (x, y), r_comp)
        pygame.draw.circle(surface, COLOR_RADAR_RING, (x, y), r_comp, 1)

        # North Arrow Pointer
        arrow_points = [(x, y - r_comp + 4), (x - 5, y + 2), (x + 5, y + 2)]
        pygame.draw.polygon(surface, COLOR_TEXT_PRIMARY, arrow_points)
        pygame.draw.polygon(surface, COLOR_ACCENT_ALERT, [(x, y + r_comp - 4), (x - 4, y - 1), (x + 4, y - 1)])

        lbl = self.font_degree.render("N", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl, (x - lbl.get_width() // 2, y - r_comp - 12))
