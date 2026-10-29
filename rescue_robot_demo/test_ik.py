"""Unit tests for the simulator inverse-kinematics solver.

Run from this directory:
    python -m unittest test_ik.py -v

These tests validate software behavior only; they do not verify real servo
orientation, linkage dimensions, calibration, or physical reachability.
"""
import math
import unittest

from ik import QuadrupedIK


class QuadrupedIKTests(unittest.TestCase):
    def setUp(self):
        self.ik = QuadrupedIK()

    def test_typical_workspace_target_is_reachable(self):
        result = self.ik.solve(80, 0, -100)
        self.assertTrue(result.reachable, result.reason)
        self.assertEqual(result.reason, "OK")
        for angle in (result.coxa, result.femur, result.tibia):
            self.assertTrue(math.isfinite(angle))
        self.assertTrue(self.ik.COXA_MIN <= result.coxa <= self.ik.COXA_MAX)
        self.assertTrue(self.ik.FEMUR_MIN <= result.femur <= self.ik.FEMUR_MAX)
        self.assertTrue(self.ik.TIBIA_MIN <= result.tibia <= self.ik.TIBIA_MAX)

    def test_out_of_reach_target_is_rejected(self):
        result = self.ik.solve(200, 0, -90)
        self.assertFalse(result.reachable)
        self.assertEqual(result.reason, "OUT_OF_REACH")

    def test_coxa_joint_limit_is_reported(self):
        # atan2(200, -10) places the coxa angle beyond the configured limit.
        result = self.ik.solve(-10, 200, -100)
        self.assertFalse(result.reachable)
        self.assertEqual(result.reason, "JOINT_LIMIT")

    def test_symmetric_lateral_targets_produce_finite_results(self):
        left = self.ik.solve(80, 20, -100)
        right = self.ik.solve(80, -20, -100)
        for result in (left, right):
            for angle in (result.coxa, result.femur, result.tibia):
                self.assertTrue(math.isfinite(angle))
        self.assertAlmostEqual(left.coxa + right.coxa, 180.0, places=3)
        self.assertAlmostEqual(left.femur, right.femur, places=3)
        self.assertAlmostEqual(left.tibia, right.tibia, places=3)

    def test_zero_distance_is_rejected_without_exception(self):
        result = self.ik.solve(35, 0, 0)
        self.assertFalse(result.reachable)
        self.assertEqual(result.reason, "OUT_OF_REACH")


if __name__ == "__main__":
    unittest.main()
