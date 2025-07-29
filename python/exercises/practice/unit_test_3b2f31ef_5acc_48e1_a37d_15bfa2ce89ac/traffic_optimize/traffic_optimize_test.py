import unittest
from traffic_optimize import optimize_traffic_lights

class TestTrafficOptimize(unittest.TestCase):
    def test_simple_intersection(self):
        num_intersections = 1
        road_segments = [(0, 1, 10), (1, 0, 10)]
        traffic_lights = {
            0: [
                [(0, 1)],
                [(1, 0)]
            ]
        }
        vehicle_arrival_rates = {(0, 1): 0.5, (1, 0): 0.5}
        time_horizon = 60
        switch_time = 5
        
        schedule = optimize_traffic_lights(
            num_intersections,
            road_segments,
            traffic_lights,
            vehicle_arrival_rates,
            time_horizon,
            switch_time
        )
        
        self.assertIn(0, schedule)
        self.assertEqual(len(schedule[0]), time_horizon // switch_time)
        for light in schedule[0]:
            self.assertIn(light, [0, 1])

    def test_multiple_intersections(self):
        num_intersections = 3
        road_segments = [
            (0, 1, 15),
            (1, 2, 15),
            (2, 0, 15),
            (1, 0, 10),
            (2, 1, 10)
        ]
        traffic_lights = {
            0: [
                [(0, 1)],
                [(2, 0)]
            ],
            1: [
                [(1, 2)],
                [(1, 0)]
            ],
            2: [
                [(2, 0)],
                [(2, 1)]
            ]
        }
        vehicle_arrival_rates = {
            (0, 1): 0.7,
            (1, 2): 0.6,
            (2, 0): 0.5,
            (1, 0): 0.3,
            (2, 1): 0.2
        }
        time_horizon = 120
        switch_time = 10
        
        schedule = optimize_traffic_lights(
            num_intersections,
            road_segments,
            traffic_lights,
            vehicle_arrival_rates,
            time_horizon,
            switch_time
        )
        
        for intersection in [0, 1, 2]:
            self.assertIn(intersection, schedule)
            self.assertEqual(len(schedule[intersection]), time_horizon // switch_time)
            for light in schedule[intersection]:
                self.assertIn(light, [0, 1])

    def test_capacity_constraints(self):
        num_intersections = 2
        road_segments = [(0, 1, 5), (1, 0, 5)]
        traffic_lights = {
            0: [
                [(0, 1)],
                [(1, 0)]
            ],
            1: [
                [(1, 0)],
                [(0, 1)]
            ]
        }
        vehicle_arrival_rates = {(0, 1): 1.0, (1, 0): 1.0}
        time_horizon = 30
        switch_time = 3
        
        schedule = optimize_traffic_lights(
            num_intersections,
            road_segments,
            traffic_lights,
            vehicle_arrival_rates,
            time_horizon,
            switch_time
        )
        
        for intersection in [0, 1]:
            self.assertIn(intersection, schedule)
            self.assertEqual(len(schedule[intersection]), time_horizon // switch_time)

    def test_switch_time_constraint(self):
        num_intersections = 1
        road_segments = [(0, 1, 20)]
        traffic_lights = {
            0: [
                [(0, 1)],
                []
            ]
        }
        vehicle_arrival_rates = {(0, 1): 0.1}
        time_horizon = 10
        switch_time = 2
        
        schedule = optimize_traffic_lights(
            num_intersections,
            road_segments,
            traffic_lights,
            vehicle_arrival_rates,
            time_horizon,
            switch_time
        )
        
        self.assertEqual(len(schedule[0]), time_horizon // switch_time)
        for i in range(1, len(schedule[0])):
            self.assertNotEqual(schedule[0][i], schedule[0][i-1])

    def test_empty_network(self):
        num_intersections = 0
        road_segments = []
        traffic_lights = {}
        vehicle_arrival_rates = {}
        time_horizon = 60
        switch_time = 5
        
        schedule = optimize_traffic_lights(
            num_intersections,
            road_segments,
            traffic_lights,
            vehicle_arrival_rates,
            time_horizon,
            switch_time
        )
        
        self.assertEqual(schedule, {})

if __name__ == '__main__':
    unittest.main()