
import unittest

from config import BASE, VICTIM, OBSTACLES
from core import Pathfinder, RescueCore
from gait import GaitPlanner
from safety import SafetyManager


class RescueRobotTests(unittest.TestCase):
    def test_pathfinder_reaches_victim(self):
        path = Pathfinder(24, 16, OBSTACLES).find(BASE, VICTIM)
        self.assertTrue(path)
        self.assertEqual(path[0], BASE)
        self.assertEqual(path[-1], VICTIM)

    def test_modes(self):
        robot = RescueCore(24, 16, OBSTACLES, BASE, VICTIM)
        for mode in robot.MODES:
            robot.set_mode(mode)
            self.assertEqual(robot.mode, mode)

    def test_rescue_cycle(self):
        robot = RescueCore(24, 16, OBSTACLES, BASE, VICTIM)
        robot.set_mode("RESCUE")

        reached_victim = False
        for _ in range(500):
            robot.step(0.05)
            if robot.robot == VICTIM and not robot.found:
                robot.report_found()
                reached_victim = True
            if robot.found and robot.robot == BASE:
                break

        self.assertTrue(reached_victim)
        self.assertTrue(robot.found)
        self.assertEqual(robot.robot, BASE)


class V2Tests(unittest.TestCase):
    def test_safety(self):
        safety = SafetyManager()
        self.assertEqual(safety.allow_motion(100), (True, "OK"))
        safety.stop("test")
        self.assertEqual(safety.allow_motion(100), (False, "EMERGENCY_STOP"))
        self.assertFalse(safety.resume(10)["ok"])
        self.assertTrue(safety.resume(100)["ok"])

    def test_gait(self):
        gait = GaitPlanner()
        gait.set_moveset("WALK")
        targets = gait.update(dt=0.1)
        self.assertEqual(set(targets), {"FL", "FR", "RL", "RR"})

        for target in targets.values():
            self.assertGreaterEqual(target.z, -90.0)
            self.assertLessEqual(target.z, -68.0)
            self.assertLessEqual(abs(target.x), 15.0)

        gait.set_moveset("IDLE")
        idle = gait.update(dt=0.1)
        self.assertTrue(all(t.phase == "STANCE" for t in idle.values()))


if __name__ == "__main__":
    unittest.main()
