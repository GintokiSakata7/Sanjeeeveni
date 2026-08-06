"""
Adaptive Smart Radar Person Detection System
Multi-Threaded Background Radar Scanning Engine (One-by-One Discovery)
"""

import threading
import time
from radar_sweep import RadarSweep
from radius_manager import RadiusManager
from target import BaseTargetProvider, SimulatedTargetProvider
from detector import Detector, DetectionEvent
from tracker import Tracker


class ScannerThread(threading.Thread):
    """
    Worker thread discovering candidate target points ONE BY ONE
    as the sweep beam rotates and expands across the radar scope.
    """

    def __init__(self, sweep: RadarSweep, radius_mgr: RadiusManager,
                 target_provider: SimulatedTargetProvider, detector: Detector, tracker: Tracker):
        super().__init__(daemon=True)
        self.sweep = sweep
        self.radius_mgr = radius_mgr
        self.target_provider = target_provider
        self.detector = detector
        self.tracker = tracker

        self.lock = threading.RLock()
        self.running = True
        self.is_scanning = True

        self.scan_count = 0
        self.search_time = 0.0
        self.newly_discovered_events: list[DetectionEvent] = []

    def stop(self):
        self.running = False

    def run(self):
        last_time = time.time()

        while self.running:
            now = time.time()
            dt = now - last_time
            last_time = now

            with self.lock:
                if self.is_scanning:
                    self.search_time += dt

                    # 1. Update Target motions
                    self.target_provider.update(dt)

                    # 2. Update High-Speed Sweep Beam Physics
                    self.sweep.update(dt_factor=dt * 60.0)

                    # 3. Check for 360° Sweep Revolution completion
                    if self.sweep.completed_full_scan:
                        self.sweep.reset_full_scan_flag()
                        self.scan_count += 1

                        # If no YES-confirmed target is within range, expand search radius (50m -> 100m -> 150m...)
                        targets = self.target_provider.get_all_targets()
                        has_yes_in_range = any(
                            t.status == "YES" and self.radius_mgr.is_in_range(t.distance_m)
                            for t in targets
                        )
                        if not has_yes_in_range:
                            self.radius_mgr.expand()

                    # 4. DYNAMIC ONE-BY-ONE TARGET DISCOVERY
                    new_targets = self.target_provider.check_dynamic_discovery(
                        sweep_angle=self.sweep.angle,
                        active_radius_m=self.radius_mgr.current_radius,
                        current_time=now
                    )

                    # 5. Perform Beam Arc Intersection Detection against discovered targets
                    discovered_targets = self.target_provider.get_all_targets()
                    events = self.detector.check_detections(
                        sweep_angle=self.sweep.angle,
                        active_radius_m=self.radius_mgr.current_radius,
                        targets=discovered_targets,
                        current_time=now
                    )

                    if events:
                        self.newly_discovered_events = events

                    # 6. Update Shortest-Distance Target Tracking Logic
                    self.tracker.update_tracking(
                        active_radius_m=self.radius_mgr.current_radius,
                        targets=discovered_targets,
                        timestamp=now
                    )

                # Smoothly interpolate active radius display
                self.radius_mgr.update(lerp_speed=0.1)

            time.sleep(0.016)

    def reset_system(self):
        """Resets all thread state, search radius (50m), scan count, and targets."""
        with self.lock:
            self.sweep.angle = 0.0
            self.radius_mgr.reset()
            self.target_provider.relocate_targets()
            self.scan_count = 0
            self.search_time = 0.0
            self.newly_discovered_events = []
