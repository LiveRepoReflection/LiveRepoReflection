import unittest
from fleet_pathing.fleet_pathing import calculate_routes

class TestFleetPathing(unittest.TestCase):
    def test_single_vehicle_no_obstacles(self):
        graph = {
            0: [(1, {'length': 100, 'speed_limit': 30})],
            1: [(0, {'length': 100, 'speed_limit': 30}), (2, {'length': 200, 'speed_limit': 40})],
            2: [(1, {'length': 200, 'speed_limit': 40})]
        }
        vehicles = [{'vehicle_id': 1, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2}]
        static_obstacles = []
        
        result = calculate_routes(graph, vehicles, static_obstacles)
        self.assertEqual(result, {1: [0, 1, 2]})

    def test_multiple_vehicles_no_collision(self):
        graph = {
            0: [(1, {'length': 100, 'speed_limit': 30})],
            1: [(0, {'length': 100, 'speed_limit': 30}), (2, {'length': 200, 'speed_limit': 40})],
            2: [(1, {'length': 200, 'speed_limit': 40})]
        }
        vehicles = [
            {'vehicle_id': 1, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2},
            {'vehicle_id': 2, 'current_location': 1, 'destination': 0, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2}
        ]
        static_obstacles = []
        
        result = calculate_routes(graph, vehicles, static_obstacles)
        self.assertEqual(result, {1: [0, 1, 2], 2: [1, 0]})

    def test_collision_avoidance(self):
        graph = {
            0: [(1, {'length': 100, 'speed_limit': 30})],
            1: [(0, {'length': 100, 'speed_limit': 30}), (2, {'length': 100, 'speed_limit': 30})],
            2: [(1, {'length': 100, 'speed_limit': 30})]
        }
        vehicles = [
            {'vehicle_id': 1, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2},
            {'vehicle_id': 2, 'current_location': 2, 'destination': 0, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2}
        ]
        static_obstacles = []
        
        result = calculate_routes(graph, vehicles, static_obstacles)
        # One vehicle should wait or take alternative path
        self.assertTrue(result[1] != [0, 1, 2] or result[2] != [2, 1, 0])

    def test_static_obstacles(self):
        graph = {
            0: [(1, {'length': 100, 'speed_limit': 30})],
            1: [(0, {'length': 100, 'speed_limit': 30}), (2, {'length': 200, 'speed_limit': 40})],
            2: [(1, {'length': 200, 'speed_limit': 40})]
        }
        vehicles = [{'vehicle_id': 1, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2}]
        static_obstacles = [1]
        
        result = calculate_routes(graph, vehicles, static_obstacles)
        self.assertEqual(result, {1: None})

    def test_no_possible_route(self):
        graph = {
            0: [(1, {'length': 100, 'speed_limit': 30})],
            1: [(0, {'length': 100, 'speed_limit': 30})],
            2: [(3, {'length': 100, 'speed_limit': 30})],
            3: [(2, {'length': 100, 'speed_limit': 30})]
        }
        vehicles = [{'vehicle_id': 1, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2}]
        static_obstacles = []
        
        result = calculate_routes(graph, vehicles, static_obstacles)
        self.assertEqual(result, {1: None})

    def test_vehicle_prioritization(self):
        graph = {
            0: [(1, {'length': 100, 'speed_limit': 30})],
            1: [(0, {'length': 100, 'speed_limit': 30}), (2, {'length': 100, 'speed_limit': 30})],
            2: [(1, {'length': 100, 'speed_limit': 30})]
        }
        vehicles = [
            {'vehicle_id': 1, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2},
            {'vehicle_id': 2, 'current_location': 0, 'destination': 2, 'speed': 10, 'safety_radius': 15, 'acceleration_rate': 2}
        ]
        static_obstacles = []
        
        result = calculate_routes(graph, vehicles, static_obstacles)
        # Vehicle 1 should get priority
        self.assertEqual(result[1], [0, 1, 2])
        self.assertNotEqual(result[2], [0, 1, 2])

if __name__ == '__main__':
    unittest.main()