import unittest
from config import BASE, VICTIM, OBSTACLES
from core import Pathfinder, RescueCore
class RescueRobotTests(unittest.TestCase):
    def test_pathfinder_reaches_victim(self):
        path=Pathfinder(24,16,OBSTACLES).find(BASE,VICTIM)
        self.assertTrue(path); self.assertEqual(path[0],BASE); self.assertEqual(path[-1],VICTIM)
    def test_modes(self):
        robot=RescueCore(24,16,OBSTACLES,BASE,VICTIM)
        for mode in robot.MODES:
            robot.set_mode(mode); self.assertEqual(robot.mode,mode)
if __name__=="__main__": unittest.main()
