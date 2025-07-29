import unittest
from vehicle_network import route_vehicles

def is_valid_path(path, start, end, road_dict):
    """
    Check if the path starts with start, ends with end and each consecutive pair is a valid directed edge.
    road_dict is a dict mapping from (u, v) to (length, congestion).
    """
    if not path:
        return False
    if path[0] != start or path[-1] != end:
        return False
    for i in range(len(path) - 1):
        if (path[i], path[i+1]) not in road_dict:
            return False
    return True

class VehicleNetworkTest(unittest.TestCase):
    def setUp(self):
        # Helper: Use this to construct a road dict for verification.
        self.road_dict = {}

    def construct_road_dict(self, roads):
        d = {}
        for u, v, length, congestion in roads:
            d[(u, v)] = (length, congestion)
        return d

    def test_single_vehicle_direct_road(self):
        num_intersections = 2
        roads = [
            (0, 1, 10, 0)
        ]
        vehicle_routes = [
            (0, 1)
        ]
        max_vehicles_per_road = 1
        energy_limit = 100
        self.road_dict = self.construct_road_dict(roads)
        result = route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit)
        # Expect a direct route [0, 1]
        self.assertEqual(len(result), 1)
        self.assertTrue(is_valid_path(result[0], 0, 1, self.road_dict))

    def test_multi_vehicle_no_conflict(self):
        num_intersections = 4
        roads = [
            (0, 1, 3, 1),
            (1, 2, 4, 2),
            (2, 3, 5, 1),
            (0, 2, 8, 1),
            (1, 3, 10, 2)
        ]
        # Two vehicles with non-overlapping routes possible.
        vehicle_routes = [
            (0, 3),
            (0, 2)
        ]
        max_vehicles_per_road = 2
        energy_limit = 100
        self.road_dict = self.construct_road_dict(roads)
        result = route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit)
        self.assertEqual(len(result), 2)
        for idx, (s, e) in enumerate(vehicle_routes):
            # For vehicles with a non-empty route, validate the path correctness.
            path = result[idx]
            if path:
                self.assertTrue(is_valid_path(path, s, e, self.road_dict))
            else:
                # If route is empty, then no valid path was found.
                self.fail("Expected a valid route for vehicle starting at {} and ending at {}".format(s, e))

    def test_vehicle_blocked_by_capacity(self):
        # Test scenario where capacity constraints force a vehicle to wait or block the path.
        # In this test setup, we expect that one of the vehicles might not find a feasible route.
        num_intersections = 3
        roads = [
            (0, 1, 5, 3),
            (1, 2, 5, 3),
            (0, 2, 15, 0)
        ]
        # Two vehicles competing for the same short but congested route.
        vehicle_routes = [
            (0, 2),
            (0, 2)
        ]
        max_vehicles_per_road = 1  # Only one vehicle can be on any road at a time.
        energy_limit = 50
        self.road_dict = self.construct_road_dict(roads)
        result = route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit)
        self.assertEqual(len(result), 2)
        # At least one vehicle may be forced to take the longer alternate route or be blocked.
        for idx, (s, e) in enumerate(vehicle_routes):
            path = result[idx]
            if path:
                self.assertTrue(is_valid_path(path, s, e, self.road_dict))
            else:
                # An empty path indicates the vehicle could not reach destination within energy limit or due to capacity.
                self.assertEqual(path, [])

    def test_energy_limit_exceeded(self):
        # Test scenario where the energy limit is too small for any vehicle to reach the destination.
        num_intersections = 4
        roads = [
            (0, 1, 10, 2),
            (1, 2, 10, 2),
            (2, 3, 10, 2),
            (0, 3, 50, 5)
        ]
        vehicle_routes = [
            (0, 3)
        ]
        max_vehicles_per_road = 2
        energy_limit = 15  # Too low energy limit for any route.
        self.road_dict = self.construct_road_dict(roads)
        result = route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit)
        self.assertEqual(len(result), 1)
        # Expect an empty route since energy limit is exceeded.
        self.assertEqual(result[0], [])

    def test_complex_network(self):
        # A more comprehensive test with multiple intersections and vehicles.
        num_intersections = 6
        roads = [
            (0, 1, 4, 1),
            (1, 2, 6, 1),
            (2, 3, 2, 3),
            (3, 5, 3, 1),
            (0, 4, 10, 0),
            (4, 3, 2, 2),
            (1, 4, 3, 1),
            (4, 2, 2, 2),
            (2, 5, 8, 1)
        ]
        vehicle_routes = [
            (0, 5),
            (0, 5),
            (1, 3)
        ]
        max_vehicles_per_road = 2
        energy_limit = 100
        self.road_dict = self.construct_road_dict(roads)
        result = route_vehicles(num_intersections, roads, vehicle_routes, max_vehicles_per_road, energy_limit)
        self.assertEqual(len(result), 3)
        for idx, (s, e) in enumerate(vehicle_routes):
            path = result[idx]
            # Allow empty path if routing fails, but if not empty, verify correctness.
            if path:
                self.assertTrue(is_valid_path(path, s, e, self.road_dict))
            else:
                self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()