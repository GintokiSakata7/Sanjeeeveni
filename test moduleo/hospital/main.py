"""
Adaptive Smart Radar Navigator - Main Application Entry Point
Accept/Reject Hospital Search Edition: Auto-detects GPS location, searches for nearest hospitals
starting at 50m radius, shows Accept/Reject buttons for each hospital.
Search ONLY stops when a hospital accepts. If 2+ accept, picks shortest distance.
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
from response_manager import ResponseManager
from detector import TargetDetector
from radar import RadarCanvas
from animation import AnimationManager
from ui import TelemetryUI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class AdaptiveRadarApp:
    """Main Application Controller with Accept/Reject hospital search flow."""

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            logging.warning(f"Audio mixer notice: {e}")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Adaptive Smart Radar Navigator - Hospital Accept/Reject Search")
        self.clock = pygame.time.Clock()

        # Instantiate System Modules
        self.gps_manager = GPSManager()
        self.searcher = HospitalSearcher()
        self.radius_manager = RadiusManager()
        self.response_manager = ResponseManager()
        self.detector = TargetDetector()
        self.radar_canvas = RadarCanvas()
        self.animation_mgr = AnimationManager()
        self.ui_panel = TelemetryUI()

        # Application State
        self.targets = []  # All discovered hospitals (for radar display)
        self.search_meta = {
            "is_searching": False,
            "latency_ms": 0.0,
            "error": None,
            "from_cache": False,
            "specialty": "Hospital Care"
        }
        self.is_running = True
        self.last_auto_refresh = time.time()
        self.search_lock = threading.Lock()

        # Flags for search thread coordination
        self._search_waiting_for_responses = False
        self._search_should_expand = threading.Event()

        # Sweep Discovery State
        self.pending_discovery_ids = set()
        self.pending_discovery_hospitals = {}

        # Modal Input State
        self.is_input_active = False
        self.input_mode = "disease"  # "disease" or "location"
        self.input_buffer = ""

        # Default Disease Search Query set to 'ear' (ENT / Ear Care)
        self.searcher.set_disease_query("ear")
        self.animation_mgr.add_notification("PRESS [D] OR [SPACE] TO SEARCH HOSPITALS...", duration=5.0)

        # Auto Start Routine
        threading.Thread(target=self._auto_start_routine, daemon=True).start()

    def _auto_start_routine(self):
        time.sleep(0.8)
        self.start_search_async()

    def run(self):
        """Main 60 FPS execution loop."""
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0

            # 1. Input Events
            self._handle_events()

            # 2. Update States
            self.radar_canvas.update_sweep(dt)
            self.animation_mgr.update(dt)
            self.radius_manager.update(lerp_speed=0.1)

            gps_data = self.gps_manager.get_status()
            current_radius = self.radius_manager.current_radius

            # 3. Check if all current hospitals responded and need expansion
            self._check_auto_expansion()

            # 4. Render Frame Graphics
            self.screen.fill(COLOR_BG)

            # Radar Canvas with active range ring
            radius_str = self.radius_manager.format_radius()
            self.radar_canvas.draw(
                self.screen,
                active_radius_str=radius_str,
                target_count=len(self.targets),
                is_locked=self.radius_manager.target_locked,
                status_msg=self.gps_manager.get_status()["status_msg"],
                displayed_radius=self.radius_manager.displayed_radius,
                max_radius=float(current_radius)
            )


            # Target Reticles and Radar Sweep Discovery
            for idx, tgt in enumerate(self.targets):
                # Scale projection to current active search radius for perfect synchronization
                sx, sy, is_inside = self.detector.gps_to_radar(
                    gps_data["lat"], gps_data["lon"],
                    tgt["lat"], tgt["lon"],
                    tgt["distance"], tgt["bearing"],
                    float(current_radius)
                )
                
                tgt_id = str(tgt.get("id", tgt.get("name", "")))
                is_swept = self.detector.is_target_swept(tgt["bearing"], self.radar_canvas.sweep_angle)

                with self.search_lock:
                    if is_swept and tgt_id in self.pending_discovery_ids:
                        self.pending_discovery_ids.remove(tgt_id)
                        h_data = self.pending_discovery_hospitals.pop(tgt_id)
                        newly_added = self.response_manager.add_hospitals([h_data])
                        if newly_added:
                            self.animation_mgr.play_ping()
                            self.animation_mgr.trigger_detection_ripple(sx, sy)
                            self.animation_mgr.add_notification(
                                f"FOUND: {h_data['name']} — PLEASE RESPOND",
                                color=(0, 255, 180), duration=4.0
                            )

                with self.search_lock:
                    is_pending = tgt_id in self.pending_discovery_ids

                # ONLY render hospital target blip if it has been discovered by the sweep beam!
                if not is_pending:
                    is_winner = (
                        self.response_manager.final_hospital is not None and
                        str(self.response_manager.final_hospital.get("id", self.response_manager.final_hospital.get("name", ""))) == tgt_id
                    )
                    status_str = self.response_manager.responses.get(tgt_id, "PENDING")
                    dist_str = self.radius_manager.format_radius(tgt["distance"])

                    self.animation_mgr.draw_target_reticle(
                        self.screen, sx, sy,
                        is_locked=is_winner,
                        name=tgt["name"],
                        dist_str=dist_str,
                        status=status_str
                    )




            # Shockwave Rings
            self.animation_mgr.draw_expanding_rings(self.screen)

            # Sidebar Panel (with response_manager for accept/reject UI)
            self.ui_panel.draw_panel(
                self.screen,
                gps_data=gps_data,
                search_meta=self.search_meta,
                targets=self.targets,
                active_radius_str=radius_str,
                is_locked=self.radius_manager.target_locked,
                active_disease_query=self.searcher.active_disease_query,
                response_manager=self.response_manager
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

    def _check_auto_expansion(self):
        """
        Checks if all currently pending hospitals have responded.
        If all rejected and none accepted, automatically triggers radius expansion.
        """
        if not self.response_manager.is_search_active:
            return
        if self.response_manager.is_resolved():
            return

        with self.search_lock:
            if len(self.pending_discovery_ids) > 0:
                return

        if self.response_manager.get_total_count() == 0:
            return

        # If all hospitals have responded (none pending)
        if self.response_manager.all_current_responded():
            accepted_count = self.response_manager.get_accepted_count()
            if accepted_count == 0:
                # All rejected — trigger expansion
                self._search_should_expand.set()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if click hit any Accept/Reject button
                mouse_x, mouse_y = event.pos
                clicked = self.ui_panel.check_button_click(mouse_x, mouse_y)
                if clicked:
                    hospital_id, action = clicked
                    self._handle_hospital_response(hospital_id, action)

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
                                self._reset_and_start_search()
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
                        self._full_reset()
                        self.animation_mgr.add_notification("SEARCH RESET — PRESS [D] TO SEARCH AGAIN")
                    elif event.key == pygame.K_l:
                        self.gps_manager.refresh_location_async()
                        self.animation_mgr.add_notification("AUTO REFRESHING GPS LOCATION...")
                        self._reset_and_start_search()

    def _handle_hospital_response(self, hospital_id: str, action: str):
        """Handles an Accept or Reject click for a hospital."""
        if action == "accept":
            winner = self.response_manager.accept(hospital_id)
            if winner:
                # A hospital accepted — lock the search
                self.radius_manager.lock_accepted()
                win_name = winner.get("name", "Hospital")
                win_dist = self.response_manager.format_distance(winner.get("distance", 0))
                self.animation_mgr.add_notification(
                    f"✅ HOSPITAL ACCEPTED: {win_name} ({win_dist})",
                    color=(0, 255, 140), duration=6.0
                )
                self.search_meta["is_searching"] = False

                # Export result
                self.searcher.export_to_json(
                    [winner], "found_hospitals.json"
                )
                logging.info(f"Search complete! Winner: {win_name} at {win_dist}")

        elif action == "reject":
            self.response_manager.reject(hospital_id)
            h_data = self.response_manager.hospital_data.get(hospital_id, {})
            h_name = h_data.get("name", "Hospital")
            self.animation_mgr.add_notification(
                f"❌ {h_name} REJECTED",
                color=(255, 60, 80), duration=2.5
            )

    def _full_reset(self):
        """Completely resets the search state."""
        self.radius_manager.reset()
        self.response_manager.reset()
        self.response_manager.is_search_active = False
        self.searcher.reset_found()
        self.targets = []
        self.pending_discovery_ids.clear()
        self.pending_discovery_hospitals.clear()
        self.search_meta["is_searching"] = False
        self._search_waiting_for_responses = False
        self._search_should_expand.clear()

    def _reset_and_start_search(self):
        """Resets state and starts a fresh search."""
        self._full_reset()
        self.start_search_async()

    def _resolve_location_and_search(self, query: str):
        success = self.gps_manager.resolve_custom_location(query)
        if success:
            g_status = self.gps_manager.get_status()
            self.animation_mgr.add_notification(f"LOCATION SET: {g_status['location_name']}", color=(0, 255, 180))
            self._reset_and_start_search()
        else:
            self.animation_mgr.add_notification(f"FAILED TO RESOLVE LOCATION: '{query}'", color=(255, 60, 100))

    def start_search_async(self):
        if self.search_meta["is_searching"]:
            return
        thread = threading.Thread(target=self._search_thread_worker, daemon=True)
        thread.start()

    def _search_thread_worker(self):
        """
        Accept/Reject Search Loop:

        1. Query hospitals at current radius
        2. New hospitals found? → Add to response_manager as PENDING, show on UI
        3. Wait for user to click Accept/Reject on all pending hospitals
        4. Any accepted? → Pick shortest distance → STOP
        5. All rejected? → Expand radius → Go to step 1
        6. No new hospitals? → Expand radius → Go to step 1
        7. Repeat until accepted or max radius (50km) reached
        """
        with self.search_lock:
            self.search_meta["is_searching"] = True

        self.response_manager.reset()
        self.searcher.reset_found()
        self.radius_manager.reset()

        lat, lon = self.gps_manager.get_coordinates()

        while self.response_manager.is_search_active:
            current_r = self.radius_manager.current_radius
            radius_str = self.radius_manager.format_radius()

            self.animation_mgr.add_notification(
                f"SCANNING RADIUS: {radius_str} FOR [{self.searcher.active_disease_query.upper()}]...",
                duration=2.5
            )

            # Query hospitals at current radius
            res = self.searcher.query_nearby(lat, lon, current_r)

            with self.search_lock:
                self.search_meta["latency_ms"] = res["latency_ms"]
                self.search_meta["error"] = res["error"]
                self.search_meta["from_cache"] = res["from_cache"]
                self.search_meta["specialty"] = res.get("specialty", "Hospital Care")

            # Update radar display with ALL hospitals found
            all_targets = res["targets"]
            if all_targets:
                self.targets = all_targets

            # Get only NEW hospitals not already in response_manager
            new_hospitals = res.get("new_targets", [])

            if new_hospitals:
                with self.search_lock:
                    for h in new_hospitals:
                        h_id = str(h.get("id", h.get("name", "")))
                        self.pending_discovery_ids.add(h_id)
                        self.pending_discovery_hospitals[h_id] = h
                
                self.animation_mgr.trigger_expansion_ring()

                # Wait for user to respond to all pending hospitals
                # The _check_auto_expansion() in the main loop will set _search_should_expand
                # when all hospitals are rejected
                self._search_waiting_for_responses = True
                self._search_should_expand.clear()

                # Wait until either:
                # 1. A hospital is accepted (is_search_active becomes False)
                # 2. All hospitals rejected (_search_should_expand is set)
                while self.response_manager.is_search_active:
                    if self.response_manager.is_resolved():
                        # A hospital accepted — search is done!
                        break

                    if self._search_should_expand.is_set():
                        # All rejected — break out to expand
                        self._search_should_expand.clear()
                        break

                    time.sleep(0.1)

                self._search_waiting_for_responses = False

                # Check if resolved (accepted)
                if self.response_manager.is_resolved():
                    break  # Search complete!

                # All rejected — need to expand
                expanded = self.radius_manager.force_expand()
                if expanded:
                    new_r_str = self.radius_manager.format_radius()
                    self.animation_mgr.trigger_expansion_ring()
                    self.animation_mgr.add_notification(
                        f"ALL REJECTED AT {radius_str} → EXPANDING TO {new_r_str}",
                        color=(255, 180, 0), duration=3.0
                    )
                    time.sleep(1.0)
                else:
                    # Max radius reached
                    self.animation_mgr.add_notification(
                        f"MAX RADIUS (50 km) REACHED — NO HOSPITAL ACCEPTED",
                        color=(255, 60, 100), duration=6.0
                    )
                    self.response_manager.is_search_active = False
                    break

            else:
                # No new hospitals found at this radius — pause for 1s scan, then expand
                time.sleep(1.0)
                expanded = self.radius_manager.force_expand()
                if expanded:
                    new_r_str = self.radius_manager.format_radius()
                    self.animation_mgr.trigger_expansion_ring()
                    self.animation_mgr.add_notification(
                        f"NO [{self.searcher.active_disease_query.upper()}] AT {radius_str} → {new_r_str}",
                        duration=2.0
                    )
                    time.sleep(1.0)
                else:
                    self.animation_mgr.add_notification(
                        f"MAX RADIUS REACHED — NO [{self.searcher.active_disease_query.upper()}] HOSPITALS",
                        color=(255, 60, 100), duration=6.0
                    )
                    self.response_manager.is_search_active = False
                    break


        with self.search_lock:
            self.search_meta["is_searching"] = False
            self.last_auto_refresh = time.time()


if __name__ == "__main__":
    app = AdaptiveRadarApp()
    app.run()
