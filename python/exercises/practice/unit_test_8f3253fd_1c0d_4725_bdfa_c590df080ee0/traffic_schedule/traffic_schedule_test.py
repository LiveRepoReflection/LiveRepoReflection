import unittest
from traffic_schedule import optimize_traffic_lights

class TrafficScheduleTest(unittest.TestCase):
    def setUp(self):
        # A simple network with 3 intersections, each with 2 incoming roads.
        self.network_simple = {
            1: {'incoming': [(2, 500, 50), (3, 600, 40)], 'outgoing': [(4, 700, 60), (5, 800, 50)]},
            2: {'incoming': [(1, 500, 50), (6, 400, 30)], 'outgoing': [(7, 900, 40), (8, 300, 20)]},
            3: {'incoming': [(1, 600, 40), (9, 700, 50)], 'outgoing': [(10, 500, 30), (11, 600, 40)]}
        }
        self.traffic_flow_simple = {
            (2, 4): 100,
            (3, 5): 80,
            (1, 7): 120,
            (6, 8): 90,
            (1, 10): 70,
            (9, 11): 110
        }
        self.min_green_time = 15
        self.max_green_time = 60
        self.yellow_time = 5
        self.total_simulation_time = 3600  # 1 hour

        # A more complex network to test edge cases (different structure, larger numbers)
        self.network_complex = {
            10: {'incoming': [(20, 400, 60), (30, 550, 50)], 'outgoing': [(40, 800, 70), (50, 900, 65)]},
            20: {'incoming': [(10, 400, 60), (60, 300, 45)], 'outgoing': [(70, 600, 55), (80, 750, 50)]},
            30: {'incoming': [(10, 550, 50), (90, 650, 60)], 'outgoing': [(100, 850, 70), (110, 950, 60)]},
            40: {'incoming': [(10, 800, 70), (120, 700, 55)], 'outgoing': [(130, 500, 45), (140, 550, 50)]}
        }
        self.traffic_flow_complex = {
            (20, 40): 150,
            (30, 50): 130,
            (10, 70): 160,
            (60, 80): 140,
            (10, 100): 120,
            (90, 110): 155,
            (10, 130): 100,
            (120, 140): 90
        }

    def validate_schedule_structure(self, schedule, network):
        # Ensure every intersection in network exists in schedule
        self.assertEqual(set(schedule.keys()), set(network.keys()))
        for intersection_id, phases in schedule.items():
            incoming_count = len(network[intersection_id]['incoming'])
            # Ensure schedule is non-empty list of tuples
            self.assertIsInstance(phases, list)
            self.assertGreater(len(phases), 0)
            for phase in phases:
                # Each phase should be a tuple of (incoming_road_index, duration)
                self.assertIsInstance(phase, tuple)
                self.assertEqual(len(phase), 2)
                road_index, duration = phase
                # Check that the incoming road index is valid (0 or 1 for two incoming roads)
                self.assertIsInstance(road_index, int)
                self.assertTrue(0 <= road_index < incoming_count,
                                f"Intersection {intersection_id} has invalid incoming road index: {road_index}")
                # Check that duration is an integer and within constraints
                self.assertIsInstance(duration, int)
                self.assertGreaterEqual(duration, self.min_green_time)
                self.assertLessEqual(duration, self.max_green_time)

    def test_schedule_structure_simple(self):
        schedule = optimize_traffic_lights(self.network_simple, self.traffic_flow_simple,
                                           self.min_green_time, self.max_green_time,
                                           self.yellow_time, self.total_simulation_time)
        self.validate_schedule_structure(schedule, self.network_simple)

    def test_schedule_structure_complex(self):
        schedule = optimize_traffic_lights(self.network_complex, self.traffic_flow_complex,
                                           self.min_green_time, self.max_green_time,
                                           self.yellow_time, self.total_simulation_time)
        self.validate_schedule_structure(schedule, self.network_complex)

    def test_all_intersections_covered(self):
        # Create a network with multiple intersections and verify schedule covers all keys
        network = {
            1: {'incoming': [(2, 300, 40), (3, 350, 45)], 'outgoing': [(4, 500, 50), (5, 600, 55)]},
            2: {'incoming': [(1, 300, 40), (6, 400, 50)], 'outgoing': [(7, 450, 45), (8, 350, 40)]},
            3: {'incoming': [(1, 350, 45), (9, 500, 50)], 'outgoing': [(10, 550, 55), (11, 600, 60)]},
            4: {'incoming': [(2, 500, 50), (12, 400, 45)], 'outgoing': [(13, 700, 60), (14, 800, 65)]}
        }
        traffic_flow = {
            (2, 4): 80,
            (3, 5): 90,
            (1, 7): 70,
            (6, 8): 60,
            (1, 10): 50,
            (9, 11): 65,
            (2, 13): 75,
            (12, 14): 55
        }
        schedule = optimize_traffic_lights(network, traffic_flow, self.min_green_time,
                                           self.max_green_time, self.yellow_time,
                                           self.total_simulation_time)
        self.assertEqual(set(schedule.keys()), set(network.keys()))
        self.validate_schedule_structure(schedule, network)

    def test_green_time_limits(self):
        # Test that each returned duration is between min and max green times
        schedule = optimize_traffic_lights(self.network_simple, self.traffic_flow_simple,
                                           self.min_green_time, self.max_green_time,
                                           self.yellow_time, self.total_simulation_time)
        for phases in schedule.values():
            for _, duration in phases:
                self.assertGreaterEqual(duration, self.min_green_time)
                self.assertLessEqual(duration, self.max_green_time)

if __name__ == '__main__':
    unittest.main()