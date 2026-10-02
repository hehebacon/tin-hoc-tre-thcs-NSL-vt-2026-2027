from heapq import heappush, heappop

from gait import GaitPlanner, JumpPlanner
from ik import QuadrupedIK


DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class Pathfinder:
    def __init__(self, width, height, obstacles, terrain=None):
        self.width = int(width)
        self.height = int(height)
        self.obstacles = set(obstacles)
        self.terrain = terrain or {}

    def valid(self, point):
        x, y = point
        return (
            0 <= x < self.width
            and 0 <= y < self.height
            and point not in self.obstacles
        )

    def cost(self, point):
        slope = abs(float(self.terrain.get(point, 0.0)))
        return 1.0 + slope / 15.0

    def find(self, start, goal):
        if not self.valid(start) or not self.valid(goal):
            return []

        frontier = []
        heappush(frontier, (0.0, start))
        came = {start: None}
        cost = {start: 0.0}

        while frontier:
            _, current = heappop(frontier)
            if current == goal:
                break

            for dx, dy in DIRS:
                nxt = (current[0] + dx, current[1] + dy)
                if not self.valid(nxt):
                    continue

                new_cost = cost[current] + self.cost(nxt)
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    priority = (
                        new_cost
                        + abs(nxt[0] - goal[0])
                        + abs(nxt[1] - goal[1])
                    )
                    heappush(frontier, (priority, nxt))
                    came[nxt] = current

        if goal not in came:
            return []

        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came[cur]

        return list(reversed(path))


class RescueCore:
    MODES = (
        "PATROL",
        "SEARCH",
        "RESCUE",
        "FOLLOW",
        "AVOID",
        "EXPLORE",
        "INSPECT",
        "DELIVER",
        "RECHARGE",
        "RETURN_HOME",
        "OSINT",
        "AUTONOMOUS",
        "DEMO",
        "CALIBRATION",
        "CLIMB",
        "JUMP",
    )

    def __init__(self, width, height, obstacles, base, victim):
        terrain = {
            (9, 3): 12.0,
            (10, 3): 12.0,
            (11, 3): 12.0,
            (18, 6): 12.0,
            (19, 6): 12.0,
            (19, 7): 12.0,
        }

        self.pathfinder = Pathfinder(width, height, obstacles, terrain)
        self.base = tuple(base)
        self.victim = tuple(victim)
        self.robot = self.base

        self.mode = "PATROL"
        self.path = []
        self.found = False
        self.searching = False
        self.emergency_stop = False

        self.gait = GaitPlanner()
        self.jump = JumpPlanner()
        self.ik = QuadrupedIK()

        # Gait.snapshot() is intentionally serializable. The core needs
        # LegTarget objects, so use update() here instead of snapshot().
        self.last_leg_targets = self.gait.update(0.05, moving=False)
        self.last_joint_angles = self.ik.solve_all(self.last_leg_targets)

        self.patrol_points = [
            self.base,
            (self.base[0] + 4, self.base[1]),
            (self.base[0] + 4, self.base[1] + 5),
            (self.base[0], self.base[1] + 5),
        ]
        self.patrol_points = [
            p for p in self.patrol_points if self.pathfinder.valid(p)
        ] or [self.base]

        self.patrol_index = 0
        self.last_target = None
        self.search_radius = 0
        self.wall_climb_driver_ready = False
        self.log = ["SYSTEM READY"]

    def log_event(self, message):
        message = str(message)
        if not self.log or self.log[0] != message:
            self.log.insert(0, message)
            self.log = self.log[:20]

    def set_mode(self, mode):
        if mode not in self.MODES:
            return False

        self.mode = mode
        self.path = []
        self.last_target = None
        self.searching = mode in ("RESCUE", "OSINT")

        if mode == "JUMP":
            self.gait.set_moveset("IDLE")
            self.jump.start()
        elif mode in ("PATROL", "RETURN_HOME", "DELIVER", "RECHARGE"):
            self.jump.stop()
            self.gait.set_moveset("STABLE_WALK")
        elif mode == "RESCUE":
            self.jump.stop()
            self.gait.set_moveset("RESCUE")
        elif mode in ("EXPLORE", "DEMO", "AUTONOMOUS"):
            self.jump.stop()
            self.gait.set_moveset("CRUISE")
        elif mode in ("FOLLOW", "AVOID", "SEARCH", "INSPECT", "OSINT"):
            self.jump.stop()
            self.gait.set_moveset("SEARCH")
        elif mode == "CLIMB":
            self.jump.stop()
            self.gait.set_moveset("IDLE")
            self.log_event("WALL CLIMB STANDBY - HARDWARE DRIVER REQUIRED")
        elif mode == "CALIBRATION":
            self.jump.stop()
            self.gait.set_moveset("IDLE")
            self.log_event("CALIBRATION MODE")

        self.log_event(f"MODE -> {mode}")
        return True

    def set_target(self, target):
        target = tuple(target)
        self.last_target = target
        self.path = self.pathfinder.find(self.robot, target)
        return bool(self.path)

    def stop(self):
        self.emergency_stop = True
        self.path = []
        self.gait.set_moveset("IDLE")
        self.jump.stop()
        self.log_event("EMERGENCY STOP")

    def resume(self):
        self.emergency_stop = False
        self.log_event("MOTION RESUMED")

    def return_home(self):
        if self.emergency_stop:
            self.log_event("RETURN HOME BLOCKED BY E-STOP")
            return False

        self.set_target(self.base)
        self.log_event("RETURN HOME REQUESTED")
        return bool(self.path) or self.robot == self.base

    def terrain_at(self):
        return {
            "slope_deg": round(
                abs(float(self.pathfinder.terrain.get(self.robot, 0.0))), 1
            ),
            "type": "SLOPE" if self.robot in self.pathfinder.terrain else "FLAT",
            "traversable": self.robot not in self.pathfinder.obstacles,
        }

    def _select_target(self):
        if self.mode == "CLIMB":
            return self.robot

        if self.mode == "PATROL":
            target = self.patrol_points[self.patrol_index]
            if self.robot == target:
                self.patrol_index = (
                    (self.patrol_index + 1) % len(self.patrol_points)
                )
                target = self.patrol_points[self.patrol_index]
            return target

        if self.mode in ("RESCUE", "AUTONOMOUS"):
            return self.base if self.found else self.victim

        if self.mode == "RETURN_HOME":
            return self.base

        return self.base

    def _update_motion_targets(self, dt, moving):
        self.last_leg_targets = self.gait.update(dt, moving=moving)
        self.last_joint_angles = self.ik.solve_all(self.last_leg_targets)

    def step(self, dt=0.05):
        dt = max(0.001, min(0.1, float(dt)))

        if self.emergency_stop:
            self._update_motion_targets(dt, moving=False)
            return

        if self.mode == "JUMP":
            jump_state = self.jump.update(dt)
            self.last_leg_targets = {
                leg: self.jump.leg_pose(leg) for leg in self.gait.LEGS
            }
            self.last_joint_angles = self.ik.solve_all(self.last_leg_targets)

            if jump_state["phase"] == "DONE" or self.jump.done:
                self.mode = "PATROL"
                self.gait.set_moveset("STABLE_WALK")
                self.log_event("JUMP COMPLETE -> STABLE_WALK")
            return

        if self.mode in ("CLIMB", "CALIBRATION"):
            self._update_motion_targets(dt, moving=False)
            return

        target = self._select_target()

        if self.mode == "OSINT" and self.robot == self.base:
            self.searching = True
            self.log_event("PUBLIC DATA SCAN ACTIVE")

        if self.path and len(self.path) > 1:
            self.path.pop(0)
            self.robot = self.path[0]
            self.search_radius += 1
        elif self.path == [self.robot]:
            self.path = []

        if not self.path and self.robot != target:
            self.set_target(target)

        moving = bool(self.path)
        self._update_motion_targets(dt, moving=moving)

    def report_found(self):
        if self.found:
            return

        self.found = True
        self.searching = False
        self.path = []
        self.last_target = self.base
        self.gait.set_moveset("RESCUE")
        self.log_event(f"PERSON FOUND @ {self.victim}")

    def reset(self):
        self.robot = self.base
        self.path = []
        self.found = False
        self.searching = False
        self.emergency_stop = False
        self.patrol_index = 0
        self.mode = "PATROL"
        self.last_target = None
        self.search_radius = 0
        self.jump.stop()
        self.gait.reset()
        self.last_leg_targets = self.gait.update(0.05, moving=False)
        self.last_joint_angles = self.ik.solve_all(self.last_leg_targets)
        self.log = ["SYSTEM RESET"]
