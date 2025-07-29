import unittest
from traffic_control import optimize_signal_timings

class TestTrafficControl(unittest.TestCase):
    def test_basic_case(self):
        intersection_state = [
            {
                "approach_name": "North",
                "through_queue": 50,
                "left_queue": 20,
                "right_queue": 10,
                "through_arrival_rate": 0.8,
                "left_arrival_rate": 0.3,
                "right_arrival_rate": 0.2,
            },
            {
                "approach_name": "South",
                "through_queue": 40,
                "left_queue": 15,
                "right_queue": 12,
                "through_arrival_rate": 0.7,
                "left_arrival_rate": 0.25,
                "right_arrival_rate": 0.22,
            },
            {
                "approach_name": "East",
                "through_queue": 60,
                "left_queue": 25,
                "right_queue": 8,
                "through_arrival_rate": 0.9,
                "left_arrival_rate": 0.4,
                "right_arrival_rate": 0.15,
            },
            {
                "approach_name": "West",
                "through_queue": 35,
                "left_queue": 18,
                "right_queue": 11,
                "through_arrival_rate": 0.6,
                "left_arrival_rate": 0.35,
                "right_arrival_rate": 0.2,
            },
        ]
        result = optimize_signal_timings(intersection_state, 60, 120, 10)
        self._validate_result(result, 60, 120, 10)

    def test_minimum_cycle_length(self):
        intersection_state = [
            {
                "approach_name": "North",
                "through_queue": 5,
                "left_queue": 2,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
            {
                "approach_name": "South",
                "through_queue": 4,
                "left_queue": 1,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
            {
                "approach_name": "East",
                "through_queue": 6,
                "left_queue": 2,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
            {
                "approach_name": "West",
                "through_queue": 3,
                "left_queue": 1,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
        ]
        result = optimize_signal_timings(intersection_state, 60, 120, 10)
        self._validate_result(result, 60, 120, 10)
        self.assertEqual(sum(result.values()), 60)  # Should use minimum cycle length

    def test_maximum_cycle_length(self):
        intersection_state = [
            {
                "approach_name": "North",
                "through_queue": 100,
                "left_queue": 40,
                "right_queue": 20,
                "through_arrival_rate": 1.5,
                "left_arrival_rate": 0.6,
                "right_arrival_rate": 0.4,
            },
            {
                "approach_name": "South",
                "through_queue": 90,
                "left_queue": 35,
                "right_queue": 25,
                "through_arrival_rate": 1.4,
                "left_arrival_rate": 0.55,
                "right_arrival_rate": 0.45,
            },
            {
                "approach_name": "East",
                "through_queue": 120,
                "left_queue": 50,
                "right_queue": 15,
                "through_arrival_rate": 1.8,
                "left_arrival_rate": 0.8,
                "right_arrival_rate": 0.3,
            },
            {
                "approach_name": "West",
                "through_queue": 80,
                "left_queue": 40,
                "right_queue": 25,
                "through_arrival_rate": 1.2,
                "left_arrival_rate": 0.7,
                "right_arrival_rate": 0.4,
            },
        ]
        result = optimize_signal_timings(intersection_state, 60, 120, 10)
        self._validate_result(result, 60, 120, 10)
        self.assertEqual(sum(result.values()), 120)  # Should use maximum cycle length

    def test_empty_queues(self):
        intersection_state = [
            {
                "approach_name": "North",
                "through_queue": 0,
                "left_queue": 0,
                "right_queue": 0,
                "through_arrival_rate": 0.0,
                "left_arrival_rate": 0.0,
                "right_arrival_rate": 0.0,
            },
            {
                "approach_name": "South",
                "through_queue": 0,
                "left_queue": 0,
                "right_queue": 0,
                "through_arrival_rate": 0.0,
                "left_arrival_rate": 0.0,
                "right_arrival_rate": 0.0,
            },
            {
                "approach_name": "East",
                "through_queue": 0,
                "left_queue": 0,
                "right_queue": 0,
                "through_arrival_rate": 0.0,
                "left_arrival_rate": 0.0,
                "right_arrival_rate": 0.0,
            },
            {
                "approach_name": "West",
                "through_queue": 0,
                "left_queue": 0,
                "right_queue": 0,
                "through_arrival_rate": 0.0,
                "left_arrival_rate": 0.0,
                "right_arrival_rate": 0.0,
            },
        ]
        result = optimize_signal_timings(intersection_state, 60, 120, 10)
        self._validate_result(result, 60, 120, 10)
        # Should distribute time equally when no traffic
        for duration in result.values():
            self.assertAlmostEqual(duration, 15, delta=1)

    def test_single_approach_heavy_traffic(self):
        intersection_state = [
            {
                "approach_name": "North",
                "through_queue": 200,
                "left_queue": 80,
                "right_queue": 40,
                "through_arrival_rate": 3.0,
                "left_arrival_rate": 1.2,
                "right_arrival_rate": 0.8,
            },
            {
                "approach_name": "South",
                "through_queue": 5,
                "left_queue": 2,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
            {
                "approach_name": "East",
                "through_queue": 5,
                "left_queue": 2,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
            {
                "approach_name": "West",
                "through_queue": 5,
                "left_queue": 2,
                "right_queue": 1,
                "through_arrival_rate": 0.1,
                "left_arrival_rate": 0.05,
                "right_arrival_rate": 0.02,
            },
        ]
        result = optimize_signal_timings(intersection_state, 60, 120, 10)
        self._validate_result(result, 60, 120, 10)
        # North should get significantly more time
        self.assertGreater(result["North"], 50)

    def _validate_result(self, result, min_cycle, max_cycle, min_green):
        # Check all approaches are present
        self.assertEqual(set(result.keys()), {"North", "South", "East", "West"})
        
        # Check each approach gets at least min_green time
        for duration in result.values():
            self.assertGreaterEqual(duration, min_green)
            
        # Check total cycle length is within bounds
        total = sum(result.values())
        self.assertGreaterEqual(total, min_cycle)
        self.assertLessEqual(total, max_cycle)

if __name__ == '__main__':
    unittest.main()