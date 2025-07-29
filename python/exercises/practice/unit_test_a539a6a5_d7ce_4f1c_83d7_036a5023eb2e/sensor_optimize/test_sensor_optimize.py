import unittest
import numpy as np
from sensor_optimize import optimize_sensor_network

class TestSensorOptimize(unittest.TestCase):
    def setUp(self):
        # Basic test case with 3 sensors and 2 regions
        self.basic_case = {
            'N': 3,
            'M': 2,
            'K': 2,
            'T': 5,
            'sensor_locations': [(0, 0), (1, 1), (2, 2)],
            'sensor_ranges': [2, 2, 2],
            'region_locations': [(0.5, 0.5), (1.5, 1.5)],
            'region_importances': [10, 20]
        }

        # Edge case: single sensor covering single region
        self.single_case = {
            'N': 1,
            'M': 1,
            'K': 1,
            'T': 3,
            'sensor_locations': [(0, 0)],
            'sensor_ranges': [1],
            'region_locations': [(0.5, 0.5)],
            'region_importances': [5]
        }

        # No coverage possible case
        self.no_coverage_case = {
            'N': 2,
            'M': 1,
            'K': 2,
            'T': 2,
            'sensor_locations': [(0, 0), (10, 10)],
            'sensor_ranges': [1, 1],
            'region_locations': [(5, 5)],
            'region_importances': [10]
        }

    def test_basic_case(self):
        result = optimize_sensor_network(**self.basic_case)
        self.assertEqual(len(result), self.basic_case['T'])
        for t in range(self.basic_case['T']):
            self.assertEqual(len(result[t]), self.basic_case['N'])
            self.assertTrue(all(action in [0, 1] for action in result[t]))

    def test_single_case(self):
        result = optimize_sensor_network(**self.single_case)
        self.assertEqual(len(result), self.single_case['T'])
        self.assertTrue(all(len(actions) == 1 for actions in result))

    def test_no_coverage_case(self):
        result = optimize_sensor_network(**self.no_coverage_case)
        self.assertEqual(len(result), self.no_coverage_case['T'])
        # Should return all sleep actions since coverage is impossible
        self.assertTrue(all(action == 0 for actions in result for action in actions))

    def test_battery_constraint(self):
        result = optimize_sensor_network(**self.basic_case)
        battery = [100] * self.basic_case['N']
        for t in range(self.basic_case['T']):
            for j in range(self.basic_case['N']):
                if result[t][j] == 1:
                    battery[j] -= 1
                self.assertGreaterEqual(battery[j], 0)

    def test_output_format(self):
        for test_case in [self.basic_case, self.single_case, self.no_coverage_case]:
            result = optimize_sensor_network(**test_case)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), test_case['T'])
            for actions in result:
                self.assertIsInstance(actions, list)
                self.assertEqual(len(actions), test_case['N'])
                self.assertTrue(all(isinstance(action, int) for action in actions))
                self.assertTrue(all(action in [0, 1] for action in actions))

if __name__ == '__main__':
    unittest.main()