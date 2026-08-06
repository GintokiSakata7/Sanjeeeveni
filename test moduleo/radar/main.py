"""
Adaptive Smart Radar Person Detection System
Main Application Entry Point (Sweep Fetch Enforcer)
"""

import sys
import time
import numpy as np
import pygame

import config
from radar import Radar
from radar_sweep import RadarSweep
from radius_manager import RadiusManager
from target import SimulatedTargetProvider
from detector import Detector
from tracker import Tracker
from animation_manager import AnimationManager
from ui import UI
from scanner_thread import ScannerThread


def generate_beep_sound(frequency=880.0, duration=0.1, sample_rate=44100) -> pygame.mixer.Sound | None:
    """Synthesizes high-tech radar sonar ping sound effect using NumPy."""
    try:
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        sine = np.sin(2 * np.pi * frequency * t)
        envelope = np.exp(-12 * t)
        audio = (sine * envelope * 32767).astype(np.int16)
        stereo_audio = np.repeat(audio[:, np.newaxis], 2, axis=1)
        return pygame.sndarray.make_sound(stereo_audio)
    except Exception:
        return None


class AdaptiveRadarApp:
    """
    Main Pygame Application Controller enforcing the requirement:
    Target YES confirmation is ONLY permitted when the radar beam has fetched the target.
    """

    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        # Instantiate OOP Components
        self.radar = Radar()
        self.sweep = RadarSweep(sweep_speed=config.SWEEP_SPEED_DEG_PER_FRAME)
        self.radius_mgr = RadiusManager()
        self.target_provider = SimulatedTargetProvider(num_targets=6)
        self.detector = Detector()
        self.tracker = Tracker(auto_track=True)
        self.animation_mgr = AnimationManager()
        self.ui = UI()

        # Sound FX
        self.ping_sound = generate_beep_sound(frequency=950.0, duration=0.1)
        self.lock_sound = generate_beep_sound(frequency=1350.0, duration=0.25)
        self.warn_sound = generate_beep_sound(frequency=450.0, duration=0.15)
        self.last_sound_time = 0.0

        # Multi-Threaded Scanning Worker
        self.scanner_thread = ScannerThread(
            sweep=self.sweep,
            radius_mgr=self.radius_mgr,
            target_provider=self.target_provider,
            detector=self.detector,
            tracker=self.tracker
        )
        self.scanner_thread.start()

        self.running = True
        self.start_time = time.time()
        self.prev_detection_count = 0
        self.prev_locked_id = None

    def handle_events(self):
        """Processes key inputs for YES/NO confirmation, TAB cycling, and controls."""
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # ESC -> Exit
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                # Y -> Confirm Selected Target as YES (ONLY ALLOWED WHEN RADAR SWEEP HAS FETCHED IT)
                elif event.key == pygame.K_y:
                    with self.scanner_thread.lock:
                        success = self.target_provider.confirm_selected_target_yes(now)
                        if success:
                            # Halt sweep scanning upon valid fetched target YES
                            self.scanner_thread.is_scanning = False
                            self.sweep.is_scanning = False
                            if self.lock_sound:
                                self.lock_sound.play()
                        else:
                            # Target not fetched yet by radar sweep beam! Show warning!
                            curr = self.target_provider.get_selected_target()
                            tid = f"#{curr.id:02d}" if curr else ""
                            self.ui.show_warning(f"CANNOT PRESS YES FOR {tid}! WAIT FOR RADAR SWEEP BEAM TO FETCH IT", now)
                            if self.warn_sound:
                                self.warn_sound.play()

                # N -> Reject Selected Target as NO (False Alarm)
                elif event.key == pygame.K_n:
                    with self.scanner_thread.lock:
                        self.target_provider.set_selected_target_no()

                # TAB -> Cycle Target Selection focus
                elif event.key == pygame.K_TAB:
                    with self.scanner_thread.lock:
                        self.target_provider.select_next_target()

                # SPACE -> Start / Pause / Resume scanning
                elif event.key == pygame.K_space:
                    with self.scanner_thread.lock:
                        self.scanner_thread.is_scanning = not self.scanner_thread.is_scanning
                        self.sweep.is_scanning = self.scanner_thread.is_scanning

                # R -> Reset system
                elif event.key == pygame.K_r:
                    self.scanner_thread.reset_system()

                # M -> Relocate target array points
                elif event.key == pygame.K_m:
                    with self.scanner_thread.lock:
                        self.target_provider.relocate_targets()

    def update(self):
        """Main thread updates and detection audio triggers."""
        dt = self.clock.get_time() / 1000.0
        now = time.time()

        self.animation_mgr.update(dt)

        with self.scanner_thread.lock:
            det_count = self.detector.total_detections_count
            locked_target = self.tracker.locked_target

            # Trigger detection ripple when sweep intersects candidate points
            if det_count > self.prev_detection_count:
                self.prev_detection_count = det_count
                for event in self.scanner_thread.newly_discovered_events:
                    tx, ty = self.radar.polar_to_cartesian(event.distance_m, event.angle_deg)
                    self.animation_mgr.trigger_detection_ripple(tx, ty)

                if self.ping_sound and (now - self.last_sound_time > 0.3):
                    self.ping_sound.play()
                    self.last_sound_time = now

            # Audio alert when primary shortest-distance target changes
            curr_locked_id = locked_target.id if locked_target else None
            if curr_locked_id != self.prev_locked_id and curr_locked_id is not None:
                if self.lock_sound:
                    self.lock_sound.play()
            self.prev_locked_id = curr_locked_id

    def render(self):
        """Main rendering pipeline running strictly at 60 FPS."""
        self.screen.fill(config.BG_COLOR)
        now = time.time()
        time_sec = now - self.start_time

        with self.scanner_thread.lock:
            disp_radius_m = self.radius_mgr.displayed_radius
            curr_radius_m = self.radius_mgr.current_radius
            max_radius_m = self.radius_mgr.max_radius
            targets = self.target_provider.get_all_targets()
            locked_target = self.tracker.locked_target
            is_scanning = self.scanner_thread.is_scanning
            search_time = self.scanner_thread.search_time
            scan_count = self.scanner_thread.scan_count
            selected_target = self.target_provider.get_selected_target()

        # 1. Render Radar Scope Grid & Range Rings
        self.radar.render_grid(self.screen, current_active_radius_m=disp_radius_m, font_small=self.ui.font_small)

        # 2. Render Candidate Target Blips & YES/NO status tags
        self.animation_mgr.render_target_blips(
            surface=self.screen,
            radar=self.radar,
            targets=targets,
            locked_target=locked_target,
            font_small=self.ui.font_small,
            time_sec=time_sec
        )

        # 3. Render Expanding Detection Ripples
        self.animation_mgr.render_effects(self.screen)

        # 4. Render High-Speed Rotating Sweep Beam & Fading Sector Trail
        self.sweep.render(self.screen, radar=self.radar, active_radius_m=disp_radius_m)

        # 5. Render Target Tracking Rays (Primary ray to shortest distance target)
        self.tracker.render_tracking(
            surface=self.screen,
            radar=self.radar,
            font_bold=self.ui.font_bold,
            time_sec=time_sec
        )

        # 6. Render HUD Sidebar & Multi-Target Verification Table
        self.ui.render_hud(
            surface=self.screen,
            current_radius_m=curr_radius_m,
            max_radius_m=max_radius_m,
            is_scanning=is_scanning,
            targets=targets,
            locked_target=locked_target,
            search_time_sec=search_time,
            scan_count=scan_count,
            selected_target=selected_target,
            current_time=now
        )

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(config.FPS)

        self.scanner_thread.stop()
        self.scanner_thread.join(timeout=1.0)
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = AdaptiveRadarApp()
    app.run()
