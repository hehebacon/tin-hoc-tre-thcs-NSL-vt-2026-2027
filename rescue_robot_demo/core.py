from heapq import heappush, heappop
import math

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class Pathfinder:
    def __init__(self, width, height, obstacles, terrain=None):
        self.width = width
        self.height = height
        self.obstacles = set(obstacles)
        self.terrain = terrain or {}

    def valid(self, point):
        x, y = point
        return 0 <= x < self.width and 0 <= y < self.height and point not in self.obstacles

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
                    priority = new_cost + abs(nxt[0] - goal[0]) + abs(nxt[1] - goal[1])
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
    MODES = ("PATROL", "RESCUE", "OSINT", "AUTONOMOUS")

    def __init__(self, width, height, obstacles, base, victim):
        terrain = {}
        for x, y in [(9, 3), (10, 3), (11, 3), (18, 6), (19, 6), (19, 7)]:
            terrain[(x, y)] = 12.0
        self.pathfinder = Pathfinder(width, height, obstacles, terrain)
        self.base = base
        self.victim = victim
        self.robot = base
        self.mode = "PATROL"
        self.path = []
        self.found = False
        self.searching = False
        self.emergency_stop = False
        self.patrol_points = [
            base, (base[0] + 4, base[1]),
            (base[0] + 4, base[1] + 5), (base[0], base[1] + 5)
        ]
        self.patrol_index = 0
        self.last_target = None
        self.search_radius = 0
        self.log = ["SYSTEM READY"]

    def log_event(self, message):
        if not self.log or self.log[0] != message:
            self.log.insert(0, message)
            self.log = self.log[:20]

    def set_mode(self, mode):
        if mode in self.MODES:
            self.mode = mode
            self.path = []
            self.last_target = None
            self.searching = mode in ("RESCUE", "OSINT")
            self.log_event(f"MODE -> {mode}")
            return True
        return False

    def set_target(self, target):
        self.last_target = target
        self.path = self.pathfinder.find(self.robot, target)

    def stop(self):
        self.emergency_stop = True
        self.path = []
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
        return bool(self.path)

    def terrain_at(self):
        return {
            "slope_deg": round(abs(float(self.pathfinder.terrain.get(self.robot, 0.0))), 1),
            "type": "SLOPE" if self.robot in self.pathfinder.terrain else "FLAT",
            "traversable": self.robot not in self.pathfinder.obstacles,
        }

    def step(self):
        if self.emergency_stop:
            return
        if self.mode == "PATROL":
            target = self.patrol_points[self.patrol_index]
            if self.robot == target:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
                target = self.patrol_points[self.patrol_index]
                self.path = []
            if not self.path:
                self.set_target(target)
        elif self.mode == "RESCUE":
            if self.found:
                self.searching = False
                if self.robot != self.base and not self.path:
                    self.set_target(self.base)
            else:
                self.searching = True
                if not self.path:
                    self.set_target(self.victim)
        elif self.mode == "OSINT":
            if self.robot != self.base:
                if not self.path:
                    self.set_target(self.base)
            else:
                self.searching = True
                self.log_event("PUBLIC DATA SCAN ACTIVE")
        elif self.mode == "AUTONOMOUS":
            target = self.victim if not self.found else self.base
            if not self.path:
                self.set_target(target)

        if self.path and len(self.path) > 1:
            self.path.pop(0)
            self.robot = self.path[0]
            self.search_radius += 1
        elif self.path == [self.robot]:
            self.path = []

    def report_found(self):
        if not self.found:
            self.found = True
            self.searching = False
            self.path = []
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
        self.log = ["SYSTEM RESET"]
