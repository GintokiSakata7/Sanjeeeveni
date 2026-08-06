"""
Adaptive Smart Radar Navigator - Main Application Entry Point
Disease & Specialty Hospital Radar Edition: Auto-detects GPS location and searches for nearest hospitals
specialized in treating specific diseases/symptoms (e.g., 'ear', 'heart', 'eye', 'kidney', 'cancer', 'ortho', etc.).
"""

import logging
import os
import sys
import threading
import time
import pygame

# Import Modular Architecture
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, COLOR_BG, AUTO_REFRESH_INTERVAL
from gps_manager import GPSManager
from hospital_search import HospitalSearcher
from radius_manager import RadiusManager
from detector import TargetDetector
from radar import RadarCanvas
from animation import AnimationManager
from ui import TelemetryUI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class AdaptiveRadarApp:
    """Main Application Controller managing Pygame 60 FPS loop, GPS fix, & disease hospital search."""

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            logging.warning(f"Audio mixer notice: {e}")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Adaptive Smart Radar Navigator - Disease & Specialty Hospital Finder")
        self.clock = pygame.time.Clock()

        # Instantiate System Modules
        self.gps_manager = GPSManager()
        self.searcher = HospitalSearcher()
        self.radius_manager = RadiusManager()
        self.detector = TargetDetector()
        self.radar_canvas = RadarCanvas()
        self.animation_mgr = AnimationManager()
        self.ui_panel = TelemetryUI()

        # Application State
        self.targets = []
        self.search_meta = {
            "is_searching": False,
            "latency_ms": 0.0,
            "error": None,
            "from_cache": False,
            "specialty": "ENT / Ear, Nose & Throat"
        }
        self.is_running = True
        self.last_auto_refresh = time.time()
        self.search_lock = threading.Lock()

        # Modal Input State
        self.is_input_active = False
        self.input_mode = "disease"  # "disease" or "location"
        self.input_buffer = ""

        # Default Disease Search Query set to 'ear' (ENT / Ear Care)
        self.searcher.set_disease_query("ear")
        self.animation_mgr.add_notification("SEARCHING NEAREST [EAR / ENT] HOSPITALS...", duration=4.0)

        # Auto Start Routine
        threading.Thread(target=self._auto_start_routine, daemon=True).start()

    def _auto_start_routine(self):
        time.sleep(0.8)
        self.start_search_async()

    def run(self):
        """Main 60 FPS execution loop."""
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0
            now = time.time()

            # 1. Input Events
            self._handle_events()

            # 2. Auto-Refresh (Every 30s)
            if now - self.last_auto_refresh > AUTO_REFRESH_INTERVAL and not self.search_meta["is_searching"] and not self.is_input_active:
                self.start_search_async()
                self.last_auto_refresh = now

            # 3. Update States
            self.radar_canvas.update_sweep(dt)
            self.animation_mgr.update(dt)

            gps_data = self.gps_manager.get_status()
            current_radius = self.radius_manager.current_radius

            for tgt in self.targets:
                if self.detector.is_target_swept(tgt["bearing"], self.radar_canvas.sweep_angle):
                    self.animation_mgr.play_ping()
                    break

            # 4. Render Frame Graphics
            self.screen.fill(COLOR_BG)

            # Radar Canvas
            radius_str = self.radius_manager.format_radius()
            self.radar_canvas.draw(
                self.screen,
                active_radius_str=radius_str,
                target_count=len(self.targets),
                is_locked=self.radius_manager.target_locked,
                status_msg=self.gps_manager.get_status()["status_msg"]
            )

            # Target Reticles
            for idx, tgt in enumerate(self.targets):
                sx, sy, is_inside = self.detector.gps_to_radar(
                    gps_data["lat"], gps_data["lon"],
                    tgt["lat"], tgt["lon"],
                    tgt["distance"], tgt["bearing"],
                    current_radius
                )
                if is_inside:
                    is_nearest = (idx == 0) and self.radius_manager.target_locked
                    dist_str = self.radius_manager.format_radius(tgt["distance"])
                    self.animation_mgr.draw_target_reticle(self.screen, sx, sy, is_nearest, tgt["name"], dist_str)

            # Shockwave Rings
            self.animation_mgr.draw_expanding_rings(self.screen)

            # Sidebar Panel
            self.ui_panel.draw_panel(
                self.screen,
                gps_data=gps_data,
                search_meta=self.search_meta,
                targets=self.targets,
                active_radius_str=radius_str,
                is_locked=self.radius_manager.target_locked,
                active_disease_query=self.searcher.active_disease_query
            )

            # Notifications
            self.animation_mgr.draw_notifications(self.screen)

            # Modal Prompt if Active
            if self.is_input_active:
                title_prompt = "ENTER DISEASE / SYMPTOM (e.g. ear, heart, eye, kidney):" if self.input_mode == "disease" else "ENTER LOCATION / CITY / COORDINATES:"
                self.ui_panel.draw_input_modal(self.screen, self.input_buffer, title_prompt)

            # Flip Buffer
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if self.is_input_active:
                    if event.key == pygame.K_RETURN:
                        self.is_input_active = False
                        query = self.input_buffer.strip()
                        self.input_buffer = ""
                        if self.input_mode == "disease":
                            if query:
                                self.searcher.set_disease_query(query)
                                self.animation_mgr.add_notification(f"SEARCHING HOSPITALS FOR: '{query.upper()}'...")
                                self.radius_manager.reset()
                                self.start_search_async()
                        elif self.input_mode == "location":
                            if query:
                                self.animation_mgr.add_notification(f"RESOLVING LOCATION: '{query}'...")
                                threading.Thread(target=self._resolve_location_and_search, args=(query,), daemon=True).start()
                    elif event.key == pygame.K_ESCAPE:
                        self.is_input_active = False
                        self.input_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_buffer = self.input_buffer[:-1]
                    else:
                        if len(event.unicode) > 0 and event.unicode.isprintable():
                            self.input_buffer += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    elif event.key == pygame.K_d or event.key == pygame.K_SPACE:
                        self.is_input_active = True
                        self.input_mode = "disease"
                        self.input_buffer = ""
                    elif event.key == pygame.K_c:
                        self.is_input_active = True
                        self.input_mode = "location"
                        self.input_buffer = ""
                    elif event.key == pygame.K_r:
                        self.radius_manager.reset()
                        self.animation_mgr.add_notification("RADAR RADIUS RESET TO 500m")
                    elif event.key == pygame.K_l:
                        self.gps_manager.refresh_location_async()
                        self.animation_mgr.add_notification("AUTO REFRESHING GPS LOCATION...")
                        self.start_search_async()

    def _resolve_location_and_search(self, query: str):
        success = self.gps_manager.resolve_custom_location(query)
        if success:
            g_status = self.gps_manager.get_status()
            self.animation_mgr.add_notification(f"LOCATION SET: {g_status['location_name']}", color=(0, 255, 180))
            self.radius_manager.reset()
            self.start_search_async()
        else:
            self.animation_mgr.add_notification(f"FAILED TO RESOLVE LOCATION: '{query}'", color=(255, 60, 100))

    def start_search_async(self):
        if self.search_meta["is_searching"]:
            return
        thread = threading.Thread(target=self._search_thread_worker, daemon=True)
        thread.start()

    def _search_thread_worker(self):
        with self.search_lock:
            self.search_meta["is_searching"] = True

        lat, lon = self.gps_manager.get_coordinates()

        while True:
            current_r = self.radius_manager.current_radius
            res = self.searcher.query_nearby(lat, lon, current_r)

            with self.search_lock:
                self.search_meta["latency_ms"] = res["latency_ms"]
                self.search_meta["error"] = res["error"]
                self.search_meta["from_cache"] = res["from_cache"]
                self.search_meta["specialty"] = res.get("specialty", "Hospital Care")

            found_targets = res["targets"]

            if found_targets:
                self.targets = found_targets
                self.radius_manager.evaluate_search(len(found_targets))

                nearest_name = found_targets[0]["name"]
                nearest_dist = self.radius_manager.format_radius(found_targets[0]["distance"])
                dis_q = self.searcher.active_disease_query.upper()
                self.animation_mgr.add_notification(
                    f"NEAREST [{dis_q}] HOSPITAL LOCKED: {nearest_name} ({nearest_dist})",
                    color=(0, 255, 140), duration=4.0
                )
                self.searcher.export_to_json(found_targets, "found_hospitals.json")
                break
            else:
                expanded = self.radius_manager.evaluate_search(0)
                if expanded:
                    new_r_str = self.radius_manager.format_radius()
                    self.animation_mgr.trigger_expansion_ring()
                    self.animation_mgr.add_notification(f"NO [{self.searcher.active_disease_query.upper()}] HOSPITALS AT {self.radius_manager.format_radius(current_r)} -> EXPANDING TO {new_r_str}")
                    time.sleep(0.2)
                else:
                    self.animation_mgr.add_notification(f"MAX RADIUS REACHED FOR [{self.searcher.active_disease_query.upper()}].", color=(255, 60, 100))
                    break

        with self.search_lock:
            self.search_meta["is_searching"] = False
            self.last_auto_refresh = time.time()


if __name__ == "__main__":
    app = AdaptiveRadarApp()
    app.run()
