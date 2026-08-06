"""
Adaptive Smart Radar Person Detection System
HUD Overlay & Multi-Target Status Renderer (One-by-One Discovery)
"""

import math
import pygame
import config
from target import Target


class UI:
    """
    Renders military-grade HUD sidebar, multi-target status list,
    interactive YES/NO verification badges, and dynamic one-by-one discovery counters.
    """

    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas", 19, bold=True)
        self.font_bold = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_large = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_normal = pygame.font.SysFont("Consolas", 13)
        self.font_small = pygame.font.SysFont("Consolas", 11)
        self.warning_message = ""
        self.warning_time = 0.0

    def show_warning(self, msg: str, current_time: float):
        self.warning_message = msg
        self.warning_time = current_time

    def _get_cardinal(self, angle_deg: float) -> str:
        angle = angle_deg % 360.0
        dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = int((angle + 22.5) / 45.0) % 8
        return dirs[idx]

    def render_hud(self, surface: pygame.Surface,
                   current_radius_m: float,
                   max_radius_m: float,
                   is_scanning: bool,
                   targets: list[Target],
                   locked_target: Target | None,
                   search_time_sec: float,
                   scan_count: int,
                   selected_target: Target | None,
                   current_time: float):
        """Renders complete HUD panel and multi-target table."""

        # 1. Top Header Banner
        title_surf = self.font_title.render("ADAPTIVE SMART RADAR", True, config.TEXT_PRIMARY)
        sub_surf = self.font_small.render("DYNAMIC ONE-BY-ONE TARGET DISCOVERY & YES/NO VERIFICATION ENGINE", True, config.TEXT_CYAN)

        surface.blit(title_surf, (25, 18))
        surface.blit(sub_surf, (25, 42))
        pygame.draw.line(surface, config.RADAR_GREEN, (25, 60), (470, 60), 2)

        # Warning Toast Banner
        if self.warning_message and (current_time - self.warning_time < 2.5):
            w_box = pygame.Rect(25, 66, 520, 26)
            pygame.draw.rect(surface, (50, 0, 0, 220), w_box, border_radius=4)
            pygame.draw.rect(surface, config.TEXT_ALERT, w_box, 1, border_radius=4)
            w_txt = self.font_bold.render(f"⚠ {self.warning_message}", True, config.TEXT_ALERT)
            surface.blit(w_txt, (35, 71))

        # 2. Right Sidebar Panel Container
        panel_x = 885
        panel_y = 15
        panel_w = 380
        panel_h = 690

        p_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(p_surf, config.PANEL_BG, (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(p_surf, config.PANEL_BORDER, (0, 0, panel_w, panel_h), 2, border_radius=8)
        surface.blit(p_surf, (panel_x, panel_y))

        curr_y = panel_y + 15

        def draw_header(title: str, y_pos: int) -> int:
            lbl = self.font_bold.render(f"// {title}", True, config.TEXT_CYAN)
            surface.blit(lbl, (panel_x + 15, y_pos))
            pygame.draw.line(surface, config.RADAR_DARK_GREEN, (panel_x + 15, y_pos + 18), (panel_x + panel_w - 15, y_pos + 18), 1)
            return y_pos + 24

        # Find closest YES target
        yes_targets = [t for t in targets if t.status == "YES"]
        closest_yes = min(yes_targets, key=lambda t: t.distance_m) if yes_targets else None

        # --- PROMINENT CLOSEST YES TARGET BANNER ---
        if closest_yes:
            t = closest_yes
            cardinal = self._get_cardinal(t.angle_deg)

            b_rect = pygame.Rect(panel_x + 12, curr_y, panel_w - 24, 115)
            pygame.draw.rect(surface, (30, 5, 10, 240), b_rect, border_radius=6)
            pygame.draw.rect(surface, config.TARGET_SHORTEST_LOCK, b_rect, 2, border_radius=6)

            lbl1 = self.font_large.render("★ CLOSEST VERIFIED TARGET [YES] ★", True, config.TARGET_YES)
            lbl2 = self.font_bold.render(f"TARGET ID       : #{t.id:02d} ({t.label})", True, config.TEXT_PRIMARY)
            lbl3 = self.font_large.render(f"SHORTEST DISTANCE: {t.distance_m:.1f} METERS", True, config.TARGET_SHORTEST_LOCK)
            lbl4 = self.font_bold.render(f"BEARING ANGLE   : {t.angle_deg:.1f}° ({cardinal})", True, config.TEXT_CYAN)
            lbl5 = self.font_small.render("STATUS          : LOCKED (CLOSEST VERIFIED YES)", True, config.TEXT_WARN)

            surface.blit(lbl1, (panel_x + 20, curr_y + 8))
            surface.blit(lbl2, (panel_x + 20, curr_y + 32))
            surface.blit(lbl3, (panel_x + 20, curr_y + 52))
            surface.blit(lbl4, (panel_x + 20, curr_y + 74))
            surface.blit(lbl5, (panel_x + 20, curr_y + 94))

            curr_y += 125

        # --- SECTION 1: SYSTEM STATUS ---
        curr_y = draw_header("SCANNER & RADAR METRICS", curr_y)

        st_text = "[ SEARCH HALTED (TARGET VERIFIED) ]" if (not is_scanning and closest_yes) else ("[ PAUSED ]" if not is_scanning else "[ SCANNING ACTIVE ]")
        st_color = config.TEXT_ALERT if (not is_scanning and closest_yes) else (config.TEXT_WARN if not is_scanning else config.TEXT_PRIMARY)

        metrics = [
            ("Radar State:", st_text, st_color),
            ("Active Search Radius:", f"{current_radius_m:.1f} m", config.TEXT_CYAN),
            ("Discovered Points:", f"{len(targets)} / 8 (One-by-One)", config.TEXT_PRIMARY),
            ("Scan Revolutions:", f"{scan_count} Pass(es)", config.TEXT_PRIMARY),
            ("Elapsed Time:", f"{search_time_sec:.1f} s", config.TEXT_PRIMARY),
        ]

        for label, val, col in metrics:
            m_lbl = self.font_normal.render(label, True, config.TEXT_MUTED)
            m_val = self.font_bold.render(val, True, col)
            surface.blit(m_lbl, (panel_x + 15, curr_y))
            surface.blit(m_val, (panel_x + 175, curr_y))
            curr_y += 18

        curr_y += 6

        # --- SECTION 2: MULTI-TARGET FETCHING & VERIFICATION TABLE ---
        curr_y = draw_header("ONE-BY-ONE DISCOVERY TABLE", curr_y)

        h_id = self.font_small.render("ID", True, config.TEXT_CYAN)
        h_dist = self.font_small.render("DIST", True, config.TEXT_CYAN)
        h_fetch = self.font_small.render("SWEEP FETCH", True, config.TEXT_CYAN)
        h_status = self.font_small.render("VERIFY STATUS", True, config.TEXT_CYAN)

        surface.blit(h_id, (panel_x + 15, curr_y))
        surface.blit(h_dist, (panel_x + 55, curr_y))
        surface.blit(h_fetch, (panel_x + 120, curr_y))
        surface.blit(h_status, (panel_x + 225, curr_y))
        curr_y += 18

        if not targets:
            no_txt = self.font_small.render("Scanning sectors... (Awaiting point discovery)", True, config.TEXT_MUTED)
            surface.blit(no_txt, (panel_x + 15, curr_y))
            curr_y += 20
        else:
            sorted_targets = sorted(targets, key=lambda t: t.distance_m)

            for t in sorted_targets:
                is_closest_yes = (closest_yes and t.id == closest_yes.id)
                is_sel = (selected_target and t.id == selected_target.id)

                if is_closest_yes:
                    t_color = config.TARGET_SHORTEST_LOCK
                    st_str = "★ [CLOSEST YES]"
                elif t.status == "YES":
                    t_color = config.TARGET_YES
                    st_str = "[YES] (CONFIRMED)"
                elif t.status == "NO":
                    t_color = config.TARGET_NO
                    st_str = "[NO] (REJECTED)"
                else:
                    t_color = config.TARGET_PENDING
                    st_str = "[PENDING]"

                if is_sel:
                    r_rect = pygame.Rect(panel_x + 10, curr_y - 2, panel_w - 20, 18)
                    pygame.draw.rect(surface, (0, 70, 90, 180), r_rect, border_radius=3)
                    pygame.draw.rect(surface, config.TEXT_CYAN, r_rect, 1, border_radius=3)

                fetch_str = "✔ FETCHED"
                fetch_col = config.TEXT_PRIMARY

                id_txt = self.font_bold.render(f"#{t.id:02d}", True, t_color)
                dist_txt = self.font_normal.render(f"{t.distance_m:.1f}m", True, config.TEXT_PRIMARY)
                fetch_txt = self.font_bold.render(fetch_str, True, fetch_col)
                st_txt = self.font_bold.render(st_str, True, t_color)

                surface.blit(id_txt, (panel_x + 15, curr_y))
                surface.blit(dist_txt, (panel_x + 55, curr_y))
                surface.blit(fetch_txt, (panel_x + 120, curr_y))
                surface.blit(st_txt, (panel_x + 225, curr_y))

                curr_y += 18

        curr_y += 8

        # --- SECTION 3: CONTROLS & SHORTCUTS ---
        curr_y = draw_header("INTERACTIVE VERIFICATION CONTROLS", curr_y)

        controls = [
            ("Y", "Press YES (Allowed after sweep discovery)"),
            ("N", "Press NO (Reject Target)"),
            ("TAB", "Cycle Selected Target Focus"),
            ("SPACE", "Resume / Pause Radar Sweep"),
            ("R", "Reset Search Radius (50m)"),
            ("M", "Relocate Target Array Points"),
            ("ESC", "Exit Application")
        ]

        for key, desc in controls:
            k_surf = self.font_bold.render(f"[{key:^5}]", True, config.TEXT_CYAN)
            d_surf = self.font_small.render(desc, True, config.TEXT_PRIMARY)
            surface.blit(k_surf, (panel_x + 15, curr_y))
            surface.blit(d_surf, (panel_x + 85, curr_y + 2))
            curr_y += 19
