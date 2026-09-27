import unittest

from gait import GaitPlanner
from safety import SafetyManager


class V2Tests(unittest.TestCase):
    def test_safety(self):
        s = SafetyManager()
        self.assertEqual(s.allow_motion(100), (True, "OK"))
        s.stop("test")
        self.assertEqual(s.allow_motion(100), (False, "EMERGENCY_STOP"))
        self.assertFalse(s.resume(10)["ok"])
        self.assertTrue(s.resume(100)["ok"])

    def test_gait(self):
        g = GaitPlanner()
        targets = g.update(moving=True, dt=0.1)
        self.assertEqual(set(targets), {"FL", "FR", "RL", "RR"})
        for target in targets.values():
            self.assertGreaterEqual(target.z, -90.0)
            self.assertLessEqual(target.z, -65.0)
            self.assertLessEqual(abs(target.x), 15.0)


if __name__ == "__main__":
    unittest.main()
