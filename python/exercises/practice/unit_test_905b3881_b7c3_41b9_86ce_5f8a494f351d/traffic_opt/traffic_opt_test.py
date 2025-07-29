import unittest
from traffic_opt import optimize_traffic

class TrafficOptTest(unittest.TestCase):
    def test_single_intersection(self):
        city = {0: [(1, 100, 5)]}
        snapshots = [
            {(0, 1): 50}
        ]
        cycle_length = 60
        schedules = optimize_traffic(city, snapshots, cycle_length)
        self.assertIsInstance(schedules, list)
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]
        self.assertIn(0, schedule)
        self.assertIsInstance(schedule[0], dict)
        self.assertIn(1, schedule[0])
        # Check that the full cycle length is assigned
        self.assertEqual(schedule[0][1], cycle_length)
        # Check that all durations are non-negative
        self.assertGreaterEqual(schedule[0][1], 0)

    def test_multiple_intersections(self):
        city = {
            0: [(1, 100, 5), (2, 50, 10)],
            1: [(2, 75, 7)],
            2: []
        }
        snapshots = [
            {(0, 1): 50, (0, 2): 30, (1, 2): 40},
            {(0, 1): 70, (0, 2): 20, (1, 2): 60}
        ]
        cycle_length = 90
        schedules = optimize_traffic(city, snapshots, cycle_length)
        self.assertEqual(len(schedules), 2)
        for schedule in schedules:
            # For intersection 0, ensure schedule exists with expected destinations
            self.assertIn(0, schedule)
            self.assertEqual(set(schedule[0].keys()), {1, 2})
            self.assertAlmostEqual(sum(schedule[0].values()), cycle_length, places=5)
            # For intersection 1, ensure schedule exists with expected destination
            self.assertIn(1, schedule)
            self.assertEqual(set(schedule[1].keys()), {2})
            self.assertAlmostEqual(sum(schedule[1].values()), cycle_length, places=5)
            # Intersections with no outgoing roads should not appear
            self.assertNotIn(2, schedule)
            # Ensure no green light duration is negative
            for lights in schedule.values():
                for duration in lights.values():
                    self.assertGreaterEqual(duration, 0)

    def test_structure_of_schedule(self):
        city = {
            0: [(1, 50, 5), (2, 75, 8)],
            1: [(0, 60, 7), (2, 80, 4)],
            2: [(0, 70, 6)]
        }
        snapshots = [
            {(0, 1): 30, (0, 2): 20, (1, 0): 40, (1, 2): 10, (2, 0): 50}
        ]
        cycle_length = 120
        schedules = optimize_traffic(city, snapshots, cycle_length)
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]
        # Verify that each intersection with outgoing roads is scheduled correctly
        for intersection, roads in city.items():
            if roads:  # Only intersections with outgoing roads should appear
                self.assertIn(intersection, schedule)
                expected_destinations = {dest for dest, cap, ft in roads}
                self.assertEqual(set(schedule[intersection].keys()), expected_destinations)
                self.assertAlmostEqual(sum(schedule[intersection].values()), cycle_length, places=5)

    def test_multiple_snapshots(self):
        city = {
            0: [(1, 100, 5)],
            1: [(2, 50, 10)],
            2: [(0, 75, 7)]
        }
        snapshots = [
            {(0, 1): 60, (1, 2): 40, (2, 0): 30},
            {(0, 1): 80, (1, 2): 20, (2, 0): 50},
            {(0, 1): 100, (1, 2): 60, (2, 0): 70}
        ]
        cycle_length = 100
        schedules = optimize_traffic(city, snapshots, cycle_length)
        self.assertEqual(len(schedules), len(snapshots))
        for schedule in schedules:
            for intersection, roads in city.items():
                if roads:
                    self.assertIn(intersection, schedule)
                    self.assertAlmostEqual(sum(schedule[intersection].values()), cycle_length, places=5)

if __name__ == '__main__':
    unittest.main()