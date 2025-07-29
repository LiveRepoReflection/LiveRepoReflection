import unittest
import time

# It is assumed that the solution implements a class RideMatchingSystem
# with the following methods:
# - __init__(city_graph): Initializes the system with the city graph.
# - update_driver(driver_id, current_location, available, update_time): Processes a driver update.
# - update_traffic(start_node, end_node, new_travel_time, update_time): Processes a traffic update.
# - request_ride(rider_id, pickup_location, destination_location, max_wait_time, request_time): Processes a rider request.
#   Returns the matched driver_id as a string or "NO_MATCH" if no driver can reach within max_wait_time.
# - cancel_ride(rider_id): Cancels a ride request for the given rider.
# - get_match_status(rider_id): Returns the status of a rider's request. This is expected to return
#   "CANCELLED" if the ride was cancelled, or the matched driver_id if already matched.
#
# For the purposes of these tests, we simulate time with integer timestamps.

from dynamic_rides import RideMatchingSystem

class TestRideMatchingSystem(unittest.TestCase):
    def setUp(self):
        # Create a simple city graph.
        # The graph is represented as an adjacency list where each key is a node and the
        # value is a list of tuples (neighbor, travel_time).
        #
        # Graph layout:
        # 1 <--> 2: 50 seconds
        # 1 <--> 3: 100 seconds
        # 2 <--> 3: 50 seconds
        # 2 <--> 4: 100 seconds
        # 3 <--> 4: 50 seconds
        self.city_graph = {
            1: [(2, 50), (3, 100)],
            2: [(1, 50), (3, 50), (4, 100)],
            3: [(1, 100), (2, 50), (4, 50)],
            4: [(2, 100), (3, 50)]
        }
        self.system = RideMatchingSystem(self.city_graph)

    def test_single_driver_match(self):
        # Single driver available close to pickup location
        # Driver D1 is at location 2; travel time from 2 to pickup location 1 via edge (2,1) is 50 sec.
        self.system.update_driver("D1", 2, True, 1)
        result = self.system.request_ride("R1", 1, 4, 60, 2)
        self.assertEqual(result, "D1", "Expected driver D1 to be matched for rider R1.")

    def test_no_match_due_to_distance(self):
        # Driver available but too far away to meet the max wait time criteria.
        # Driver D2 is at location 4; expected shortest route from 4 to 1 is 4->2->1 = 100 + 50 = 150 sec,
        # which exceeds the rider's max wait time of 40 sec.
        self.system.update_driver("D2", 4, True, 1)
        result = self.system.request_ride("R2", 1, 3, 40, 2)
        self.assertEqual(result, "NO_MATCH", "Expected no driver to be matched for rider R2.")

    def test_multiple_driver_choose_closest(self):
        # Two drivers available; match should select the one with the shortest travel time.
        # Driver D1 is at location 2 (distance from 1 is 50 sec) and
        # Driver D2 is at location 3 (distance from 1 is 100 sec).
        self.system.update_driver("D1", 2, True, 1)
        self.system.update_driver("D2", 3, True, 1)
        result = self.system.request_ride("R3", 1, 4, 120, 2)
        self.assertEqual(result, "D1", "Expected driver D1 to be matched for rider R3 as the closest driver.")

    def test_driver_becomes_unavailable(self):
        # Driver initially available but then becomes unavailable before a ride is requested.
        self.system.update_driver("D1", 2, True, 1)
        # Driver D1 becomes unavailable.
        self.system.update_driver("D1", 2, False, 3)
        result = self.system.request_ride("R4", 1, 4, 60, 4)
        self.assertEqual(result, "NO_MATCH", "Expected no match for rider R4 since driver D1 is unavailable.")

    def test_traffic_update_influences_route(self):
        # A driver is available, and initially the travel time meets the criteria.
        self.system.update_driver("D3", 3, True, 1)
        # Rider R5 at location 1: shortest path from 3 to 1 is currently 100 sec.
        result = self.system.request_ride("R5", 1, 4, 110, 2)
        self.assertEqual(result, "D3", "Expected driver D3 to be matched for rider R5 initially.")

        # Now, update traffic so that travel times worsen:
        # Update edge from 2 to 1 to 200 sec.
        self.system.update_traffic(2, 1, 200, 3)
        # Update edge from 3 to 1 to 200 sec.
        self.system.update_traffic(3, 1, 200, 3)
        # For a new rider R6 from location 1, the available driver D3 now requires more than 110 sec.
        result2 = self.system.request_ride("R6", 1, 4, 110, 4)
        self.assertEqual(result2, "NO_MATCH", "Expected no match for rider R6 after adverse traffic updates.")

    def test_ride_cancellation(self):
        # Rider R7 requests a ride, but then cancels before the match is finalized.
        self.system.update_driver("D4", 2, True, 1)
        # Process the request.
        self.system.request_ride("R7", 1, 4, 60, 2)
        # Rider cancels the ride.
        self.system.cancel_ride("R7")
        # get_match_status is expected to return "CANCELLED" for a cancelled ride.
        status = self.system.get_match_status("R7")
        self.assertEqual(status, "CANCELLED", "Expected rider R7's request to be marked as CANCELLED after cancellation.")

if __name__ == '__main__':
    unittest.main()