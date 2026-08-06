"""
UI Module - Adaptive Smart Radar Navigator (Disease & Specialty Radar Edition)
Renders side telemetry HUD panel displaying disease/symptom query status,
nearest specialty hospital breakdown, and keyboard shortcuts.
"""

import pygame
from config import (
    TELEMETRY_PANEL_X, TELEMETRY_PANEL_Y, TELEMETRY_PANEL_WIDTH, TELEMETRY_PANEL_HEIGHT,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT_WARN, COLOR_TARGET_LOCKED, COLOR_TARGET_NORMAL
)


class TelemetryUI:
    """Manages tactical HUD panel rendering for Disease/Specialty Hospital Radar."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_section = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_body = pygame.font.SysFont("Consolas", 12, bold=False)
        self.font_small = pygame.font.SysFont("Consolas", 11, bold=False)

    def draw_panel(self, surface: pygame.Surface, gps_data: dict, search_meta: dict,
                   targets: list, active_radius_str: str, is_locked: bool, active_disease_query: str):
        """Draws the right-hand side HUD telemetry panel."""
        px, py, pw, ph = TELEMETRY_PANEL_X, TELEMETRY_PANEL_Y, TELEMETRY_PANEL_WIDTH, TELEMETRY_PANEL_HEIGHT

        # 1. Panel Background & Frame Border
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill(COLOR_PANEL_BG)
        pygame.draw.rect(panel_surf, COLOR_PANEL_BORDER, (0, 0, pw, ph), 2)
        surface.blit(panel_surf, (px, py))

        cur_y = py + 16
        x_offset = px + 18

        # Header Title
        title_surf = self.font_title.render("SPECIALTY RADAR NAVIGATOR", True, COLOR_TEXT_PRIMARY)
        surface.blit(title_surf, (x_offset, cur_y))
        cur_y += 28

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 14

        # 2. GPS Location Block
        self._draw_section_header(surface, x_offset, cur_y, "USER LOCATION TELEMETRY")
        cur_y += 20

        lat_str = f"{gps_data.get('lat', 0.0):.5f}°"
        lon_str = f"{gps_data.get('lon', 0.0):.5f}°"
        loc_name = gps_data.get("location_name", "Detecting...")

        self._draw_label_value(surface, x_offset, cur_y, "LATITUDE:", lat_str)
        self._draw_label_value(surface, x_offset + 220, cur_y, "LONGITUDE:", lon_str)
        cur_y += 20
        self._draw_label_value(surface, x_offset, cur_y, "LOCATION:", loc_name[:36], val_color=COLOR_TEXT_PRIMARY)
        cur_y += 20
        self._draw_label_value(surface, x_offset, cur_y, "STATUS:", gps_data.get("status_msg", "Ready"))
        cur_y += 28

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 14

        # 3. Active Disease / Symptom Target Banner
        specialty_title = search_meta.get("specialty", f"Query: {active_disease_query.title()}")
        self._draw_section_header(surface, x_offset, cur_y, f"DISEASE/SYMPTOM QUERY: [{active_disease_query.upper()}]")
        cur_y += 20

        lock_text = f"NEAREST {active_disease_query.upper()} HOSPITAL LOCKED" if is_locked else ("SEARCHING POIs..." if search_meta.get("is_searching") else "RADAR ACTIVE")
        lock_color = COLOR_TARGET_LOCKED if is_locked else (COLOR_ACCENT_WARN if search_meta.get("is_searching") else COLOR_TEXT_PRIMARY)

        # Status Lock Box
        l_box = pygame.Rect(x_offset, cur_y, 444, 34)
        pygame.draw.rect(surface, (20, 35, 40), l_box)
        pygame.draw.rect(surface, lock_color, l_box, 1)

        lock_surf = self.font_section.render(lock_text[:40], True, lock_color)
        surface.blit(lock_surf, (l_box.x + l_box.width // 2 - lock_surf.get_width() // 2, l_box.y + 8))
        cur_y += 44

        self._draw_label_value(surface, x_offset, cur_y, "SPECIALTY:", specialty_title[:32], val_color=COLOR_TEXT_PRIMARY)
        self._draw_label_value(surface, x_offset + 260, cur_y, "MATCHES:", str(len(targets)))
        cur_y += 28

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 14

        # 4. Discovered Specialty Hospitals Breakdown List
        self._draw_section_header(surface, x_offset, cur_y, f"NEAREST {active_disease_query.upper()} HOSPITALS")
        cur_y += 20

        if targets:
            for idx, item in enumerate(targets[:5]):
                rank_str = f"#{idx+1}"
                name_str = item["name"][:24]
                dist_str = f"{item['distance']}m"
                brg_str = f"{item['bearing']}°"
                color = COLOR_TARGET_LOCKED if idx == 0 else COLOR_TARGET_NORMAL

                rank_surf = self.font_small.render(rank_str, True, color)
                name_surf = self.font_small.render(name_str, True, COLOR_TEXT_PRIMARY)
                info_surf = self.font_small.render(f"{dist_str} ({brg_str})", True, COLOR_TEXT_SECONDARY)

                surface.blit(rank_surf, (x_offset, cur_y))
                surface.blit(name_surf, (x_offset + 30, cur_y))
                surface.blit(info_surf, (x_offset + 280, cur_y))
                cur_y += 18
            cur_y += 10
        else:
            no_tgt_surf = self.font_body.render(f"Searching nearest {active_disease_query} hospital...", True, COLOR_ACCENT_WARN)
            surface.blit(no_tgt_surf, (x_offset, cur_y))
            cur_y += 28

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 14

        # 5. Controls Legend
        self._draw_section_header(surface, x_offset, cur_y, "KEYBOARD CONTROLS")
        cur_y += 20

        controls = [
            ("D", "Search Disease/Symptom (e.g. ear)"),
            ("C", "Set Custom City/Coordinates"),
            ("L", "Auto GPS Location Fix"),
            ("R", "Reset Search Radius"),
            ("ESC", "Exit Application"),
        ]

        for i, (k, desc) in enumerate(controls):
            col_x = x_offset if i % 2 == 0 else x_offset + 220
            row_y = cur_y + (i // 2) * 18
            k_surf = self.font_small.render(f"[{k}]", True, COLOR_TEXT_PRIMARY)
            d_surf = self.font_small.render(desc, True, COLOR_TEXT_SECONDARY)
            surface.blit(k_surf, (col_x, row_y))
            surface.blit(d_surf, (col_x + 55, row_y))

    def draw_input_modal(self, surface: pygame.Surface, input_text: str, title_str: str = "ENTER DISEASE / SYMPTOM (e.g. ear, heart, eye):"):
        """Renders tactical modal prompt for entering disease/symptom or location."""
        mw, mh = 540, 140
        mx = (surface.get_width() - mw) // 2
        my = (surface.get_height() - mh) // 2

        modal_surf = pygame.Surface((mw, mh), pygame.SRCALPHA)
        modal_surf.fill((10, 20, 26, 240))
        pygame.draw.rect(modal_surf, (0, 255, 180), (0, 0, mw, mh), 2)

        title = self.font_section.render(title_str, True, COLOR_TEXT_PRIMARY)
        modal_surf.blit(title, (20, 16))

        # Input Box
        box_rect = pygame.Rect(20, 48, 500, 36)
        pygame.draw.rect(modal_surf, (18, 32, 40), box_rect)
        pygame.draw.rect(modal_surf, COLOR_PANEL_BORDER, box_rect, 1)

        disp_text = input_text + "_"
        txt_surf = self.font_title.render(disp_text, True, (255, 255, 255))
        modal_surf.blit(txt_surf, (box_rect.x + 10, box_rect.y + 6))

        sub_txt = self.font_small.render("e.g., 'ear', 'heart', 'eye', 'cancer', 'kidney', 'ortho', 'child', 'fever'", True, COLOR_TEXT_MUTED)
        modal_surf.blit(sub_txt, (20, 96))

        surface.blit(modal_surf, (mx, my))

    def _draw_section_header(self, surface: pygame.Surface, x: int, y: int, title: str):
        txt_surf = self.font_section.render(title, True, COLOR_TEXT_PRIMARY)
        surface.blit(txt_surf, (x, y))

    def _draw_label_value(self, surface: pygame.Surface, x: int, y: int, label: str, val: str, val_color=COLOR_TEXT_SECONDARY):
        lbl_surf = self.font_body.render(label, True, COLOR_TEXT_MUTED)
        val_surf = self.font_body.render(str(val), True, val_color)
        surface.blit(lbl_surf, (x, y))
        surface.blit(val_surf, (x + lbl_surf.get_width() + 6, y))
