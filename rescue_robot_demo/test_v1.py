import unittest

from config import BASE, VICTIM, OBSTACLES
from core import RescueCore, Pathfinder
from mission import MissionManager
from state_machine import StateMachine


class V1Tests(unittest.TestCase):
    def test_navigation_avoids_obstacles(self):
        path = Pathfinder(24, 16, OBSTACLES).find(BASE, VICTIM)
        self.assertTrue(path)
        self.assertEqual(path[0], BASE)
        self.assertEqual(path[-1], VICTIM)
        self.assertTrue(all(point not in OBSTACLES for point in path))

    def test_all_modes(self):
        robot = RescueCore(24, 16, OBSTACLES, BASE, VICTIM)
        for mode in robot.MODES:
            self.assertTrue(robot.set_mode(mode))
            self.assertEqual(robot.mode, mode)

    def test_safety_commands(self):
        robot = RescueCore(24, 16, OBSTACLES, BASE, VICTIM)
        robot.set_mode("RESCUE")
        robot.stop()
        self.assertTrue(robot.emergency_stop)
        robot.step()
        self.assertEqual(robot.robot, BASE)
        robot.resume()
        self.assertFalse(robot.emergency_stop)

    def test_mission_lifecycle(self):
        mission = MissionManager()
        mission.start("TEST")
        self.assertTrue(mission.active)
        mission.stop()
        self.assertFalse(mission.active)

    def test_state_machine(self):
        sm = StateMachine()
        self.assertEqual(sm.update("PATROL", False, False, False), "PATROLLING")
        self.assertEqual(sm.update("RESCUE", False, True, False), "SEARCHING")
        self.assertEqual(sm.update("RESCUE", True, False, False), "RETURNING")
        self.assertEqual(sm.update("RESCUE", True, False, True), "COMPLETE")


if __name__ == "__main__":
    unittest.main()
