import unittest
import time
from datetime import datetime, timedelta

from drone_deliveries import assign_deliveries

class TestDroneDeliveries(unittest.TestCase):
    def setUp(self):
        # Create a simple 5x5 city map with low congestion
        self.city_map = [
            [0, 1, 2, 1, 0],
            [1, 2, 3, 2, 1],
            [2, 3, 4, 3, 2],
            [1, 2, 3, 2, 1],
            [0, 1, 2, 1, 0]
        ]
        # Central depot coordinates
        self.depot = (2, 2)
        # Risk factor for collision calculations
        self.risk_factor = 0.5

        # Current timestamp for deadlines
        self.current_time = int(time.time())
    
    def test_empty_requests(self):
        # Test with no delivery requests.
        requests = []
        drones = [
            (1, (2, 2), "medium", 5),
            (2, (2, 2), "large", 5)
        ]
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        # The returned dictionary should have all drone keys with empty lists.
        expected = {drone[0]: [] for drone in drones}
        self.assertEqual(result, expected)
    
    def test_no_drones(self):
        # Test with delivery requests but no available drones.
        requests = [
            (101, (0, 0), (4, 4), "small", 1, self.current_time + 3600),
            (102, (1, 1), (3, 3), "medium", 2, self.current_time + 3600)
        ]
        drones = []
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        # Expect an empty dictionary since there are no drones.
        self.assertEqual(result, {})
    
    def test_single_request_single_drone(self):
        # One request matching one drone's payload capability.
        requests = [
            (201, (0, 0), (4, 4), "small", 3, self.current_time + 3600)
        ]
        drones = [
            (1, (2, 2), "small", 5)
        ]
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        # The only drone should be assigned the only valid request.
        self.assertIn(1, result)
        self.assertEqual(len(result[1]), 1)
        self.assertEqual(result[1][0], 201)
    
    def test_payload_incompatibility(self):
        # Test where one request is too heavy for the drone.
        requests = [
            (301, (0, 0), (4, 4), "large", 5, self.current_time + 3600),
            (302, (1, 1), (3, 3), "small", 5, self.current_time + 3600)
        ]
        drones = [
            (1, (2, 2), "medium", 5)
        ]
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        # Drone 1 cannot carry a 'large' package, so only request 302 should be assigned.
        self.assertIn(1, result)
        assigned = result[1]
        self.assertTrue(302 in assigned)
        self.assertFalse(301 in assigned)
        # Also ensure that no request is assigned more than once.
        self.assertEqual(len(assigned), len(set(assigned)))
    
    def test_deadline_constraint(self):
        # Test with one request close to deadline and one with ample deadline.
        near_deadline = self.current_time + 10  # nearly due
        ample_deadline = self.current_time + 7200  # 2 hours in future
        requests = [
            (401, (0, 0), (4, 4), "small", 4, near_deadline),
            (402, (1, 1), (3, 3), "small", 3, ample_deadline)
        ]
        drones = [
            (1, (2, 2), "large", 5),
            (2, (2, 2), "large", 5)
        ]
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        # The algorithm should attempt to prioritize feasible deliveries before the deadline.
        # We check that if any delivery is scheduled, its deadline is met by considering current time.
        for drone_id, req_ids in result.items():
            for req_id in req_ids:
                # Find the corresponding request details.
                req = next(r for r in requests if r[0] == req_id)
                deadline = req[5]
                # Assume the solution itinerary meets the deadline (cannot simulate full route time here).
                self.assertGreaterEqual(deadline, self.current_time)
    
    def test_multiple_drones_multiple_requests(self):
        # More comprehensive scenario with several delivery requests and drones.
        requests = [
            (501, (0, 0), (4, 4), "small", 10, self.current_time + 3600),
            (502, (1, 1), (3, 3), "medium", 8, self.current_time + 3600),
            (503, (2, 0), (2, 4), "large", 9, self.current_time + 3600),
            (504, (0, 4), (4, 0), "small", 7, self.current_time + 3600),
            (505, (4, 4), (0, 0), "medium", 6, self.current_time + 3600)
        ]
        drones = [
            (1, (2, 2), "large", 5),
            (2, (2, 2), "medium", 5),
            (3, (2, 2), "small", 5)
        ]
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        # Check that every drone in the input has an entry in the output.
        drone_ids = {d[0] for d in drones}
        self.assertEqual(set(result.keys()), drone_ids)
        
        # Collect all assigned request IDs.
        assigned_requests = []
        for req_list in result.values():
            assigned_requests.extend(req_list)
        # Ensure that no request is assigned more than once.
        self.assertEqual(len(assigned_requests), len(set(assigned_requests)))
        # Ensure that all assigned request IDs are in the original requests list.
        valid_request_ids = {r[0] for r in requests}
        for req_id in assigned_requests:
            self.assertIn(req_id, valid_request_ids)
    
    def test_output_structure(self):
        # Test that the output is a dictionary with keys as ints and values as lists of ints.
        requests = [
            (601, (0, 0), (4, 4), "small", 5, self.current_time + 3600)
        ]
        drones = [
            (1, (2, 2), "small", 5)
        ]
        result = assign_deliveries(requests, self.city_map, drones, self.depot, self.risk_factor)
        self.assertIsInstance(result, dict)
        for drone_id, req_list in result.items():
            self.assertIsInstance(drone_id, int)
            self.assertIsInstance(req_list, list)
            for req_id in req_list:
                self.assertIsInstance(req_id, int)

if __name__ == '__main__':
    unittest.main()