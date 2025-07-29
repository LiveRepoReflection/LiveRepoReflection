import unittest
from truck_deliveries import plan_deliveries

class TestTruckDeliveries(unittest.TestCase):

    def test_single_delivery_success(self):
        # Test case 1: Single truck, single request feasible.
        num_cities = 2
        roads = [(1, 2, 5)]
        trucks = [(1, 10)]  # (starting city, capacity)
        requests = [
            (2, (0, 10), 5)  # (destination, (start_time, end_time), weight)
        ]
        expected_total_time = 5
        expected_fulfilled = [0]
        expected_assignments = [{
            "truck": 0,
            "request": 0,
            "start_time": 0,
            "route": [1, 2]
        }]
        result = plan_deliveries(num_cities, roads, trucks, requests)
        total_time, fulfilled, assignments = result
        self.assertEqual(total_time, expected_total_time)
        self.assertEqual(fulfilled, expected_fulfilled)
        self.assertEqual(assignments, expected_assignments)

    def test_delivery_request_exceeds_capacity(self):
        # Test case 2: Truck capacity is insufficient for the request.
        num_cities = 2
        roads = [(1, 2, 5)]
        trucks = [(1, 4)]  # capacity less than requirement
        requests = [
            (2, (0, 10), 5)
        ]
        expected_total_time = -1
        expected_fulfilled = []
        expected_assignments = []
        result = plan_deliveries(num_cities, roads, trucks, requests)
        total_time, fulfilled, assignments = result
        self.assertEqual(total_time, expected_total_time)
        self.assertEqual(fulfilled, expected_fulfilled)
        self.assertEqual(assignments, expected_assignments)

    def test_truck_waits_for_time_window(self):
        # Test case 3: Truck must wait to meet the request's time window.
        num_cities = 3
        roads = [(1, 2, 3), (2, 3, 4)]
        trucks = [(1, 10)]
        requests = [
            (3, (10, 15), 5)
        ]
        # Route from 1 -> 2 -> 3 has travel time 3 + 4 = 7.
        # Truck waits until time 10 to start the delivery.
        expected_total_time = 7
        expected_fulfilled = [0]
        expected_assignments = [{
            "truck": 0,
            "request": 0,
            "start_time": 10,
            "route": [1, 2, 3]
        }]
        result = plan_deliveries(num_cities, roads, trucks, requests)
        total_time, fulfilled, assignments = result
        self.assertEqual(total_time, expected_total_time)
        self.assertEqual(fulfilled, expected_fulfilled)
        self.assertEqual(assignments, expected_assignments)

    def test_multiple_trucks_and_requests(self):
        # Test case 4: Multiple trucks and multiple requests.
        num_cities = 4
        roads = [
            (1, 2, 3), 
            (2, 3, 4), 
            (3, 4, 5), 
            (1, 4, 12),
            (2, 4, 8)
        ]
        trucks = [
            (1, 10),  # Truck 0 starts at city 1 with capacity 10
            (2, 5)    # Truck 1 starts at city 2 with capacity 5
        ]
        requests = [
            (3, (0, 8), 5),   # Request 0: destination 3, window (0,8), weight 5.
            (4, (5, 10), 4)   # Request 1: destination 4, window (5,10), weight 4.
        ]
        # Expected assignments:
        # Truck 0 takes request 0: route 1->2->3, travel time = 3+4 = 7, start time = 0.
        # Truck 1 takes request 1: route 2->4, travel time = 8, start time = 5.
        expected_total_time = 7 + 8  # 15
        expected_fulfilled = [0, 1]
        expected_assignments = [
            {
                "truck": 0,
                "request": 0,
                "start_time": 0,
                "route": [1, 2, 3]
            },
            {
                "truck": 1,
                "request": 1,
                "start_time": 5,
                "route": [2, 4]
            }
        ]
        result = plan_deliveries(num_cities, roads, trucks, requests)
        total_time, fulfilled, assignments = result
        self.assertEqual(total_time, expected_total_time)
        self.assertEqual(fulfilled, expected_fulfilled)
        self.assertEqual(assignments, expected_assignments)

    def test_no_possible_routes(self):
        # Test case 5: No route exists from truck start to request destination.
        num_cities = 3
        roads = [(1, 2, 5)]  # There is no road connecting to city 3.
        trucks = [(1, 10)]
        requests = [
            (3, (0, 10), 5)
        ]
        expected_total_time = -1
        expected_fulfilled = []
        expected_assignments = []
        result = plan_deliveries(num_cities, roads, trucks, requests)
        total_time, fulfilled, assignments = result
        self.assertEqual(total_time, expected_total_time)
        self.assertEqual(fulfilled, expected_fulfilled)
        self.assertEqual(assignments, expected_assignments)


if __name__ == '__main__':
    unittest.main()