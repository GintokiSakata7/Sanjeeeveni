"""
Adaptive Smart Radar Person Detection System
Multi-Target Detector Engine (Sweep Fetch Evaluator)
"""

import math
import random
from target import Target


class DetectionEvent:
    """Encapsulates target detection data during sweep pass."""

    def __init__(self, target: Target, confidence: float, timestamp: float):
        self.target = target
        self.confidence = confidence
        self.timestamp = timestamp
        self.distance_m = target.distance_m
        self.angle_deg = target.angle_deg


class Detector:
    """
    Evaluates sweep beam intersection against multiple candidate target points.
    Sets target.is_fetched = True when beam passes over target, enabling YES verification.
    """

    def __init__(self, beam_width_deg: float = 9.0):
        self.beam_width_deg = beam_width_deg
        self.detected_targets: dict[int, DetectionEvent] = {}
        self.total_detections_count = 0
        self.last_confidence = 96.5

    def check_detections(self, sweep_angle: float, active_radius_m: float,
                         targets: list[Target], current_time: float) -> list[DetectionEvent]:
        """
        Evaluates all target points inside active search radius intersected by sweep beam.
        Sets target.is_fetched = True upon sweep beam contact.
        """
        events = []

        for target in targets:
            if target.distance_m > active_radius_m:
                continue

            angle_diff = abs((sweep_angle - target.angle_deg + 180) % 360 - 180)

            if angle_diff <= self.beam_width_deg / 2.0:
                # Mark target as FETCHED by radar sweep beam!
                target.is_fetched = True
                target.last_fetch_time = current_time

                dist_factor = 1.0 - (target.distance_m / max(1.0, active_radius_m)) * 0.15
                snr_noise = random.uniform(-1.0, 1.0)
                conf = round(min(99.9, max(85.0, 97.0 * dist_factor + snr_noise)), 1)

                event = DetectionEvent(target=target, confidence=conf, timestamp=current_time)
                self.detected_targets[target.id] = event
                self.total_detections_count += 1
                self.last_confidence = conf
                events.append(event)

        return events
