"""
UI Module - Adaptive Smart Radar Navigator (Accept/Reject Hospital Search Edition)
Renders side telemetry HUD panel with interactive Accept/Reject buttons for each hospital,
response status indicators, and final distance selection banner.
"""

import pygame
from config import (
    TELEMETRY_PANEL_X, TELEMETRY_PANEL_Y, TELEMETRY_PANEL_WIDTH, TELEMETRY_PANEL_HEIGHT,
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT_WARN, COLOR_TARGET_LOCKED, COLOR_TARGET_NORMAL,
    COLOR_BTN_ACCEPT, COLOR_BTN_REJECT, COLOR_RESPONSE_ACCEPTED,
    COLOR_RESPONSE_REJECTED, COLOR_RESPONSE_PENDING,
    COLOR_FINAL_BANNER_BG, COLOR_FINAL_BANNER_BORDER
)


class TelemetryUI:
    """Manages tactical HUD panel rendering with Accept/Reject hospital interaction."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_section = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_body = pygame.font.SysFont("Consolas", 12, bold=False)
        self.font_small = pygame.font.SysFont("Consolas", 11, bold=False)
        self.font_btn = pygame.font.SysFont("Consolas", 11, bold=True)
        self.font_banner = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_banner_big = pygame.font.SysFont("Consolas", 22, bold=True)

        # Store button rectangles for click detection: list of (pygame.Rect, hospital_id, action)
        self.button_rects = []

    def draw_panel(self, surface: pygame.Surface, gps_data: dict, search_meta: dict,
                   targets: list, active_radius_str: str, is_locked: bool,
                   active_disease_query: str, response_manager=None):
        """Draws the right-hand side HUD telemetry panel with accept/reject cards."""
        px, py, pw, ph = TELEMETRY_PANEL_X, TELEMETRY_PANEL_Y, TELEMETRY_PANEL_WIDTH, TELEMETRY_PANEL_HEIGHT

        # Clear button rects each frame
        self.button_rects = []

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
        cur_y += 24

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 10

        # 3. Search Status Block
        self._draw_section_header(surface, x_offset, cur_y, f"DISEASE QUERY: [{active_disease_query.upper()}]")
        cur_y += 20

        # Determine status text based on response_manager state
        if response_manager and response_manager.is_resolved():
            lock_text = f"HOSPITAL ACCEPTED — SEARCH COMPLETE"
            lock_color = COLOR_RESPONSE_ACCEPTED
        elif is_locked:
            lock_text = f"NEAREST {active_disease_query.upper()} HOSPITAL LOCKED"
            lock_color = COLOR_TARGET_LOCKED
        elif search_meta.get("is_searching"):
            lock_text = "SEARCHING — WAITING FOR HOSPITAL RESPONSE..."
            lock_color = COLOR_ACCENT_WARN
        else:
            lock_text = "PRESS [D] TO START SEARCH"
            lock_color = COLOR_TEXT_PRIMARY

        # Status Lock Box
        l_box = pygame.Rect(x_offset, cur_y, 444, 30)
        pygame.draw.rect(surface, (20, 35, 40), l_box)
        pygame.draw.rect(surface, lock_color, l_box, 1)

        lock_surf = self.font_section.render(lock_text[:48], True, lock_color)
        surface.blit(lock_surf, (l_box.x + l_box.width // 2 - lock_surf.get_width() // 2, l_box.y + 7))
        cur_y += 36

        # Response counters
        if response_manager:
            counts_str = (
                f"TOTAL: {response_manager.get_total_count()}  |  "
                f"PENDING: {response_manager.get_pending_count()}  |  "
                f"ACCEPTED: {response_manager.get_accepted_count()}  |  "
                f"REJECTED: {response_manager.get_rejected_count()}"
            )
            counts_surf = self.font_small.render(counts_str, True, COLOR_TEXT_SECONDARY)
            surface.blit(counts_surf, (x_offset, cur_y))
            cur_y += 16

        self._draw_label_value(surface, x_offset, cur_y, "RADIUS:", active_radius_str)
        self._draw_label_value(surface, x_offset + 160, cur_y, "SPECIALTY:", search_meta.get("specialty", "")[:20])
        cur_y += 22

        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 10

        # 4. Hospital Response Cards (Accept/Reject)
        if response_manager and response_manager.get_total_count() > 0:
            self._draw_section_header(surface, x_offset, cur_y, "HOSPITAL RESPONSES")
            cur_y += 18

            hospitals_with_status = response_manager.get_all_hospitals_with_status()
            max_display = 5  # Show top 5 hospitals to fit panel
            for idx, (h_data, status) in enumerate(hospitals_with_status[:max_display]):
                cur_y = self._draw_hospital_card(
                    surface, x_offset, cur_y, idx + 1, h_data, status, response_manager
                )
                cur_y += 4

            if len(hospitals_with_status) > max_display:
                more_surf = self.font_small.render(
                    f"... +{len(hospitals_with_status) - max_display} more hospitals",
                    True, COLOR_TEXT_MUTED
                )
                surface.blit(more_surf, (x_offset, cur_y))
                cur_y += 16
        else:
            self._draw_section_header(surface, x_offset, cur_y, "HOSPITALS")
            cur_y += 18
            no_tgt_surf = self.font_body.render(
                f"Searching {active_disease_query} hospitals...", True, COLOR_ACCENT_WARN
            )
            surface.blit(no_tgt_surf, (x_offset, cur_y))
            cur_y += 20

        cur_y += 4
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (x_offset, cur_y), (px + pw - 18, cur_y), 1)
        cur_y += 10

        # 5. Final Selection Banner (if a hospital was accepted)
        if response_manager and response_manager.is_resolved():
            self._draw_final_banner(surface, x_offset, cur_y, response_manager)
            cur_y += 80

        # 6. Controls Legend
        remaining_space = py + ph - cur_y - 10
        if remaining_space > 60:
            self._draw_section_header(surface, x_offset, cur_y, "CONTROLS")
            cur_y += 18

            controls = [
                ("D/SPACE", "Search Disease"),
                ("C", "Set Location"),
                ("L", "GPS Refresh"),
                ("R", "Reset Search"),
                ("ESC", "Exit"),
            ]

            for i, (k, desc) in enumerate(controls):
                col_x = x_offset if i % 2 == 0 else x_offset + 220
                row_y = cur_y + (i // 2) * 16
                k_surf = self.font_small.render(f"[{k}]", True, COLOR_TEXT_PRIMARY)
                d_surf = self.font_small.render(desc, True, COLOR_TEXT_SECONDARY)
                surface.blit(k_surf, (col_x, row_y))
                surface.blit(d_surf, (col_x + len(k) * 7 + 22, row_y))

    def _draw_hospital_card(self, surface: pygame.Surface, x: int, y: int,
                             rank: int, h_data: dict, status: str, response_manager) -> int:
        """
        Draws a single hospital card with name, distance, status, and Accept/Reject buttons.
        Returns the y position after this card.
        """
        card_w = 444
        h_id = str(h_data.get("id", h_data.get("name", "")))
        name = h_data.get("name", "Unknown")[:22]
        distance = h_data.get("distance", 0)
        dist_str = response_manager.format_distance(distance)

        # Status color and label
        if status == "ACCEPTED":
            status_color = COLOR_RESPONSE_ACCEPTED
            status_label = "✅ ACCEPTED"
            card_h = 36
        elif status == "REJECTED":
            status_color = COLOR_RESPONSE_REJECTED
            status_label = "❌ REJECTED"
            card_h = 36
        else:  # PENDING
            status_color = COLOR_RESPONSE_PENDING
            status_label = "⏳ PENDING"
            card_h = 54  # Extra height for buttons

        # Card background
        card_rect = pygame.Rect(x, y, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((15, 28, 35, 200))
        pygame.draw.rect(card_surf, status_color, (0, 0, card_w, card_h), 1)
        surface.blit(card_surf, (x, y))

        # Rank + Name + Distance
        rank_color = COLOR_TARGET_LOCKED if rank == 1 else COLOR_TARGET_NORMAL
        rank_surf = self.font_small.render(f"#{rank}", True, rank_color)
        name_surf = self.font_small.render(name, True, COLOR_TEXT_PRIMARY)
        dist_surf = self.font_small.render(dist_str, True, COLOR_TEXT_SECONDARY)
        status_surf = self.font_small.render(status_label, True, status_color)

        surface.blit(rank_surf, (x + 8, y + 6))
        surface.blit(name_surf, (x + 34, y + 6))
        surface.blit(dist_surf, (x + 290, y + 6))
        surface.blit(status_surf, (x + 358, y + 6))

        # Accept/Reject Buttons (only for PENDING status)
        if status == "PENDING":
            btn_y = y + 26
            btn_h = 22

            # Accept Button
            accept_rect = pygame.Rect(x + 34, btn_y, 90, btn_h)
            pygame.draw.rect(surface, (10, 40, 30), accept_rect)
            pygame.draw.rect(surface, COLOR_BTN_ACCEPT, accept_rect, 1)
            accept_lbl = self.font_btn.render("✅ ACCEPT", True, COLOR_BTN_ACCEPT)
            surface.blit(accept_lbl, (accept_rect.x + 8, accept_rect.y + 4))
            self.button_rects.append((accept_rect, h_id, "accept"))

            # Reject Button
            reject_rect = pygame.Rect(x + 134, btn_y, 90, btn_h)
            pygame.draw.rect(surface, (40, 15, 18), reject_rect)
            pygame.draw.rect(surface, COLOR_BTN_REJECT, reject_rect, 1)
            reject_lbl = self.font_btn.render("❌ REJECT", True, COLOR_BTN_REJECT)
            surface.blit(reject_lbl, (reject_rect.x + 8, reject_rect.y + 4))
            self.button_rects.append((reject_rect, h_id, "reject"))

        return y + card_h

    def _draw_final_banner(self, surface: pygame.Surface, x: int, y: int, response_manager):
        """Draws the prominent final selection banner with hospital name and distance."""
        banner_w = 444
        banner_h = 72

        # Banner background with glow border
        banner_rect = pygame.Rect(x, y, banner_w, banner_h)
        banner_surf = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        banner_surf.fill(COLOR_FINAL_BANNER_BG + (240,))
        pygame.draw.rect(banner_surf, COLOR_FINAL_BANNER_BORDER, (0, 0, banner_w, banner_h), 2)
        surface.blit(banner_surf, (x, y))

        winner = response_manager.final_hospital
        if winner:
            win_name = winner.get("name", "Unknown Hospital")[:30]
            win_dist = response_manager.format_distance(response_manager.final_distance or 0)

            # Hospital icon + name
            title_surf = self.font_banner.render(f"🏥 SELECTED: {win_name}", True, COLOR_FINAL_BANNER_BORDER)
            surface.blit(title_surf, (x + 12, y + 12))

            # Distance display
            dist_surf = self.font_banner_big.render(f"📏 DISTANCE: {win_dist}", True, (255, 255, 255))
            surface.blit(dist_surf, (x + 12, y + 38))

    def draw_input_modal(self, surface: pygame.Surface, input_text: str,
                          title_str: str = "ENTER DISEASE / SYMPTOM (e.g. ear, heart, eye):"):
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

    def check_button_click(self, mouse_x: int, mouse_y: int):
        """
        Hit-tests if a click landed on an Accept or Reject button.
        Returns (hospital_id, "accept"/"reject") or None.
        """
        for rect, h_id, action in self.button_rects:
            if rect.collidepoint(mouse_x, mouse_y):
                return (h_id, action)
        return None

    def _draw_section_header(self, surface: pygame.Surface, x: int, y: int, title: str):
        txt_surf = self.font_section.render(title, True, COLOR_TEXT_PRIMARY)
        surface.blit(txt_surf, (x, y))

    def _draw_label_value(self, surface: pygame.Surface, x: int, y: int, label: str, val: str, val_color=COLOR_TEXT_SECONDARY):
        lbl_surf = self.font_body.render(label, True, COLOR_TEXT_MUTED)
        val_surf = self.font_body.render(str(val), True, val_color)
        surface.blit(lbl_surf, (x, y))
        surface.blit(val_surf, (x + lbl_surf.get_width() + 6, y))
