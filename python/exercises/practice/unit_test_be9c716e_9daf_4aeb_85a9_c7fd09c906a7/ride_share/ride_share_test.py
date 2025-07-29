import unittest
from ride_share import RideSharingSystem

class TestRideShareSystem(unittest.TestCase):
    def setUp(self):
        # Create an instance of the ride sharing system.
        self.system = RideSharingSystem()
        # Initialize a simple graph for tests.
        # For simplicity, add roads with (start, end) having travel_time and cost.
        # Graph structure for tests:
        # 1 -> 2, 2 -> 3, 1 -> 3, 2 -> 4, 3 -> 4, 4 -> 5
        self.system.add_road(1, 2, travel_time=3, cost=5)
        self.system.add_road(2, 3, travel_time=4, cost=7)
        self.system.add_road(1, 3, travel_time=6, cost=12)
        self.system.add_road(2, 4, travel_time=5, cost=10)
        self.system.add_road(3, 4, travel_time=5, cost=15)
        self.system.add_road(4, 5, travel_time=3, cost=8)
    
    def test_basic_matching(self):
        # Test that an available driver who meets the max_wait_time condition is assigned.
        # Setup: One driver at node 1, available.
        self.system.update_driver(driver_id=1, current_location=1, is_available=True, driver_multiplier=2)
        # Request from pickup=2, dropoff=3, max_wait_time=5.
        # Expected: The driver at node 1 should reach node 2 in 3 time units (1->2).
        # Ride cost from 2 to 3 is 7 and multiplied by 2 equals 14.
        result = self.system.process_ride_request(pickup_location=2, dropoff_location=3, max_wait_time=5)
        self.assertIsNotNone(result)
        driver_id, total_cost = result
        self.assertEqual(driver_id, 1)
        self.assertEqual(total_cost, 14)
    
    def test_no_available_driver(self):
        # Test that when no driver is available or meets wait time constraint, None is returned.
        # Setup: A driver present but not available.
        self.system.update_driver(driver_id=2, current_location=1, is_available=False, driver_multiplier=1)
        result = self.system.process_ride_request(pickup_location=2, dropoff_location=3, max_wait_time=10)
        self.assertIsNone(result)
    
    def test_multiple_drivers_tie_break(self):
        # Test scenario with multiple available drivers having same pickup travel time,
        # then choose the driver with the lowest ride cost.
        # Create two drivers at different nodes but with identical pickup travel time.
        # Driver 1: at node 2, available, multiplier=2.
        # Driver 2: at node 3, available, multiplier=1.
        self.system.update_driver(driver_id=1, current_location=2, is_available=True, driver_multiplier=2)
        self.system.update_driver(driver_id=2, current_location=3, is_available=True, driver_multiplier=1)
        # For a ride request from pickup=4, dropoff=5 with max_wait_time = 10:
        # Both drivers reach node 4 in 5 time units:
        # - For driver 1: route from 2->4 travel_time is 5, cost is 10.
        # - For driver 2: route from 3->4 travel_time is 5, cost is 15.
        # Ride segment from 4 to 5: cost is 8.
        # Total cost for driver 1 = 8 * 2 = 16, for driver 2 = 8 * 1 = 8.
        # Although both meet the wait time constraint (5 <= 10),
        # the tiebreaker selects the one with the lowest ride cost: driver 2.
        result = self.system.process_ride_request(pickup_location=4, dropoff_location=5, max_wait_time=10)
        self.assertIsNotNone(result)
        driver_id, total_cost = result
        self.assertEqual(driver_id, 2)
        self.assertEqual(total_cost, 8)
    
    def test_dynamic_road_update(self):
        # Test that a road update dynamically affects the matching outcome.
        # Setup: A driver at node 1, available, multiplier=1.
        self.system.update_driver(driver_id=3, current_location=1, is_available=True, driver_multiplier=1)
        # Initially, add a road with travel_time too high for max_wait_time:
        # Remove existing road from 1 to 2 and add a new one with travel_time 10.
        self.system.remove_road(1, 2)
        self.system.add_road(1, 2, travel_time=10, cost=10)
        # Request from pickup=2, dropoff=3 with max_wait_time=8 should return None.
        result = self.system.process_ride_request(pickup_location=2, dropoff_location=3, max_wait_time=8)
        self.assertIsNone(result)
        # Now update the road from 1 to 2 with lower travel_time.
        self.system.update_road(start_node=1, end_node=2, new_travel_time=7, new_cost=10)
        # Now the same request should be processed successfully.
        # Ride cost from 2 to 3 is 7 and multiplier is 1.
        result = self.system.process_ride_request(pickup_location=2, dropoff_location=3, max_wait_time=8)
        self.assertIsNotNone(result)
        driver_id, total_cost = result
        self.assertEqual(driver_id, 3)
        self.assertEqual(total_cost, 7)

if __name__ == '__main__':
    unittest.main()