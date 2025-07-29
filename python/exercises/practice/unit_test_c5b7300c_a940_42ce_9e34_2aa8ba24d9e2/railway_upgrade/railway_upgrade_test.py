import math
import unittest
from railway_upgrade.railway_upgrade import calculate_min_max_delay

class RailwayUpgradeTest(unittest.TestCase):
    def test_no_closure_single_trip(self):
        # Simple network with two cities and no upgrade closures.
        N = 2
        # Each track: (city1, city2, length, trains)
        tracks = [
            (0, 1, 10, [0, 5, 10, 15, 20])
        ]
        upgrade_schedule = []  # no closures
        # One passenger: (departure_city, arrival_city, desired_departure_time)
        passenger_trips = [
            (0, 1, 0)
        ]
        # Without any closures the fastest schedule can be achieved
        # so maximum delay among passengers should be 0.
        result = calculate_min_max_delay(N, tracks, upgrade_schedule, passenger_trips)
        self.assertEqual(result, 0)

    def test_with_delay_due_to_closure(self):
        # Network with three cities, where the closure on one track forces a delay.
        N = 3
        tracks = [
            # Format: (city1, city2, length, trains)
            (0, 1, 10, [10, 20, 30]),
            (1, 2, 10, [15, 25, 35])
        ]
        # Closure on track from 1 to 2 from time 10 to 20 inclusive.
        upgrade_schedule = [
            (1, 2, 10, 20)
        ]
        # Passenger trip: from 0 to 2, desired departure time 10.
        # Without any closures:
        #  - 0 -> 1: departs at 10, arrival = 10.
        #  - 1 -> 2: earliest train after 10 is at 15, so arrival = 15.
        # Earliest possible arrival = 15.
        # With closure on track (1,2), the 15 train is blocked, so passenger must take 25 instead.
        # Delay = 25 - 15 = 10.
        passenger_trips = [
            (0, 2, 10)
        ]
        result = calculate_min_max_delay(N, tracks, upgrade_schedule, passenger_trips)
        self.assertEqual(result, 10)

    def test_unreachable_trip(self):
        # Network where a passenger's destination is unreachable due to a full-day closure.
        N = 3
        tracks = [
            (0, 1, 10, [0, 10]),
            (1, 2, 10, [5, 15])
        ]
        # Closure on track (1,2) covers the entire day.
        upgrade_schedule = [
            (1, 2, 0, 1439)
        ]
        passenger_trips = [
            (0, 2, 0)
        ]
        result = calculate_min_max_delay(N, tracks, upgrade_schedule, passenger_trips)
        self.assertTrue(math.isinf(result))

    def test_multiple_passengers_no_closure(self):
        # Network with four cities and multiple passenger trips without any closures.
        N = 4
        tracks = [
            (0, 1, 5, [0, 10, 20]),
            (1, 2, 5, [1, 11, 21]),
            (2, 3, 5, [2, 12, 22]),
            (0, 3, 10, [5, 15, 25])
        ]
        upgrade_schedule = []
        passenger_trips = [
            # For trip (0, 3, 0), optimal via 0->1->2->3:
            # 0->1: departure 0, arrival 0;
            # 1->2: departure 1, arrival 1;
            # 2->3: departure 2, arrival 2.
            # Earliest arrival would be 2.
            (0, 3, 0),
            # For trip (0, 3, 10), best could be direct:
            # 0->3: departure 15, arrival 15.
            (0, 3, 10)
        ]
        # With no closures, each passenger can achieve their earliest arrival,
        # so maximum delay among passengers is 0.
        result = calculate_min_max_delay(N, tracks, upgrade_schedule, passenger_trips)
        self.assertEqual(result, 0)

    def test_alternative_routes_with_closure(self):
        # Complex scenario where a closure on the direct track forces passengers to choose an alternate route.
        N = 5
        tracks = [
            (0, 1, 5, [0, 20, 40]),
            (1, 2, 5, [10, 30, 50]),
            (2, 3, 5, [20, 40, 60]),
            (3, 4, 5, [30, 50, 70]),
            (0, 4, 10, [15, 35, 55])
        ]
        # Closure on the direct track from 0 to 4 from time 10 to 40.
        upgrade_schedule = [
            (0, 4, 10, 40)
        ]
        passenger_trips = [
            # For passenger (0,4,0): Without closures, the direct route using track (0,4)
            # would leave at 15 and arrive at 15, yielding an earliest arrival of 15.
            # Due to the closure, the direct route is delayed.
            # Instead, the alternate route 0->1->2->3->4 gives:
            # 0->1: departure 0, arrival 0;
            # 1->2: departure 10, arrival 10;
            # 2->3: departure 20, arrival 20;
            # 3->4: departure 30, arrival 30.
            # Hence, the optimal arrival becomes 30 and the delay is 30 - 15 = 15.
            (0, 4, 0)
        ]
        result = calculate_min_max_delay(N, tracks, upgrade_schedule, passenger_trips)
        self.assertEqual(result, 15)

if __name__ == '__main__':
    unittest.main()