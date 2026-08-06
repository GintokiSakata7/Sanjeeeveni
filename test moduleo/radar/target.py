"""
Adaptive Smart Radar Person Detection System
Dynamic One-by-One Target Discovery Provider
"""

from abc import ABC, abstractmethod
import math
import random
import config


class Target:
    """
    Data model representing a candidate target point on the radar.
    """

    def __init__(self, target_id: int, distance_m: float, angle_deg: float, label: str = ""):
        self.id = target_id
        self.distance_m = distance_m
        self.angle_deg = angle_deg % 360.0
        self.label = label if label else f"Target #{target_id:02d}"
        
        # Status: "PENDING", "YES", "NO"
        self.status = "PENDING"
        self.is_selected = False
        
        # Dynamic Discovery & Sweep Fetch Flags
        self.is_discovered = False  # Set True ONE BY ONE when sweep beam intersects position
        self.is_fetched = False     # Can press YES only when fetched
        self.discovery_time = 0.0
        
        # Motion parameters
        self.is_moving = random.choice([True, False])
        self.speed_m_s = random.uniform(0.8, 1.6)
        self.heading_deg = random.uniform(0, 360)

    def update_motion(self, dt: float, max_radius: float = config.MAX_RADIUS_METERS):
        if not self.is_moving or not self.is_discovered:
            return

        rad_heading = math.radians(self.heading_deg)
        rad_target = math.radians(self.angle_deg)

        x_m = self.distance_m * math.sin(rad_target) + self.speed_m_s * dt * math.sin(rad_heading)
        y_m = self.distance_m * math.cos(rad_target) + self.speed_m_s * dt * math.cos(rad_heading)

        self.distance_m = math.hypot(x_m, y_m)
        self.angle_deg = math.degrees(math.atan2(x_m, y_m)) % 360.0

        if self.distance_m > max_radius - 15:
            self.heading_deg = (self.heading_deg + 180) % 360.0
            self.distance_m = max_radius - 18


class BaseTargetProvider(ABC):
    @abstractmethod
    def get_all_targets(self) -> list[Target]:
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def relocate_targets(self):
        pass


class SimulatedTargetProvider(BaseTargetProvider):
    """
    Generates hidden potential target points and discovers them ONE BY ONE
    as the sweep beam sweeps across their location.
    """

    def __init__(self, num_targets: int = 8):
        self.num_targets = num_targets
        self.pool: list[Target] = []       # Hidden undiscovered targets
        self.discovered: list[Target] = [] # Active targets discovered one by one
        self.selected_index = 0
        self.relocate_targets()

    def get_all_targets(self) -> list[Target]:
        """Returns ONLY the targets that have been discovered so far."""
        return self.discovered

    def update(self, dt: float):
        for target in self.discovered:
            target.update_motion(dt)

    def check_dynamic_discovery(self, sweep_angle: float, active_radius_m: float, current_time: float, beam_width_deg: float = 12.0) -> list[Target]:
        """
        Discovers hidden targets ONE BY ONE as the rotating sweep beam passes over them.
        Returns list of newly discovered target points.
        """
        newly_discovered = []
        remaining_pool = []

        for target in self.pool:
            if target.distance_m <= active_radius_m:
                angle_diff = abs((sweep_angle - target.angle_deg + 180) % 360 - 180)
                if angle_diff <= beam_width_deg / 2.0:
                    # Discover target ONE BY ONE!
                    target.is_discovered = True
                    target.is_fetched = True
                    target.discovery_time = current_time
                    self.discovered.append(target)
                    newly_discovered.append(target)
                    continue

            remaining_pool.append(target)

        self.pool = remaining_pool
        return newly_discovered

    def relocate_targets(self):
        """Resets target pool with hidden candidate points for one-by-one discovery."""
        self.discovered = []
        self.pool = []

        distances = [55.0, 95.0, 140.0, 195.0, 260.0, 330.0, 400.0, 460.0]
        angles = [30.0, 110.0, 200.0, 290.0, 75.0, 160.0, 245.0, 325.0]

        for i in range(min(self.num_targets, len(distances))):
            d = distances[i] + random.uniform(-10.0, 10.0)
            a = angles[i] + random.uniform(-15.0, 15.0)
            t = Target(target_id=i + 1, distance_m=d, angle_deg=a)
            self.pool.append(t)

        self.selected_index = 0

    def select_next_target(self) -> Target | None:
        if not self.discovered:
            return None
        self.discovered[self.selected_index].is_selected = False
        self.selected_index = (self.selected_index + 1) % len(self.discovered)
        self.discovered[self.selected_index].is_selected = True
        return self.discovered[self.selected_index]

    def get_selected_target(self) -> Target | None:
        if self.discovered and 0 <= self.selected_index < len(self.discovered):
            return self.discovered[self.selected_index]
        return None

    def confirm_selected_target_yes(self, current_time: float) -> bool:
        curr = self.get_selected_target()
        if curr and curr.is_fetched:
            curr.status = "YES"
            return True
        return False

    def set_selected_target_no(self):
        curr = self.get_selected_target()
        if curr:
            curr.status = "NO"
