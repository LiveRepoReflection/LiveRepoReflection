import unittest
from transit_mapper import find_optimal_route

class TransitMapperTest(unittest.TestCase):
    def test_same_stop(self):
        # If start and end stops are the same, the arrival time should be the starting time.
        stops = {1: (0.0, 0.0)}
        routes = {}
        transfers = {}
        start_stop = 1
        end_stop = 1
        start_time = (9, 0)
        current_time = (9, 0)
        delay_updates = []
        transfer_time = 3
        self.assertEqual(find_optimal_route(stops, routes, transfers, start_stop, end_stop, start_time, current_time, delay_updates, transfer_time), (9, 0))

    def test_no_route(self):
        # When no routes or transfers are available between the stops, the function should return None.
        stops = {1: (0.0, 0.0), 2: (1.0, 1.0)}
        routes = {}
        transfers = {}
        start_stop = 1
        end_stop = 2
        start_time = (9, 0)
        current_time = (9, 0)
        delay_updates = []
        transfer_time = 3
        self.assertIsNone(find_optimal_route(stops, routes, transfers, start_stop, end_stop, start_time, current_time, delay_updates, transfer_time))

    def test_direct_route(self):
        # Simple direct route:
        # Route 101 goes from stop 1 -> 2 -> 3 with a scheduled departure at 10:00.
        # Assume travel time between consecutive stops is 5 minutes.
        # Therefore, arrival at stop 3 should be 10:00 + (5*2) = 10:10.
        stops = {
            1: (0.0, 0.0),
            2: (1.0, 1.0),
            3: (2.0, 2.0)
        }
        routes = {
            101: {
                'mode': 'bus',
                'stops': [1, 2, 3],
                'schedule': [(10, 0)]
            }
        }
        transfers = {}
        start_stop = 1
        end_stop = 3
        start_time = (9, 50)
        current_time = (9, 50)
        delay_updates = []
        transfer_time = 3
        self.assertEqual(find_optimal_route(stops, routes, transfers, start_stop, end_stop, start_time, current_time, delay_updates, transfer_time), (10, 10))

    def test_route_with_transfer(self):
        # Route with one transfer:
        # Route 201: stops [1, 2] with a departure at 09:30. (5 minutes from 1 to 2)
        # Route 202: stops [2, 3] with a departure at 09:45. (5 minutes from 2 to 3)
        # There is an implicit transfer at stop 2 which takes 3 minutes.
        # Calculations:
        # Wait until 09:30 for route 201 -> depart at 09:30, arrive at stop 2 at 09:35.
        # A transfer takes 3 minutes making the earliest boarding time 09:38.
        # Route 202 departs at 09:45, ride for 5 minutes and arrive at 09:50.
        stops = {
            1: (0.0, 0.0),
            2: (1.0, 1.0),
            3: (2.0, 2.0)
        }
        routes = {
            201: {
                'mode': 'bus',
                'stops': [1, 2],
                'schedule': [(9, 30)]
            },
            202: {
                'mode': 'train',
                'stops': [2, 3],
                'schedule': [(9, 45)]
            }
        }
        transfers = {
            # If needed, transfers between stops can be represented here.
            # For this test, transferring is implicit at stop 2 and uses a fixed transfer_time.
        }
        start_stop = 1
        end_stop = 3
        start_time = (9, 0)
        current_time = (9, 0)
        delay_updates = []
        transfer_time = 3
        self.assertEqual(find_optimal_route(stops, routes, transfers, start_stop, end_stop, start_time, current_time, delay_updates, transfer_time), (9, 50))

    def test_delay_update(self):
        # Test a direct route that is affected by a delay update.
        # Route 101 goes from stop 1 -> 2 -> 3 with a scheduled departure at 10:00.
        # Without delay, arrival would be 10:10. However, a delay of 7 minutes is added at stop 2.
        # Therefore, the vehicle will reach stop 2 at 10:05 + 7 = 10:12, and then reach stop 3 at 10:12 + 5 = 10:17.
        stops = {
            1: (0.0, 0.0),
            2: (1.0, 1.0),
            3: (2.0, 2.0)
        }
        routes = {
            101: {
                'mode': 'bus',
                'stops': [1, 2, 3],
                'schedule': [(10, 0)]
            }
        }
        transfers = {}
        start_stop = 1
        end_stop = 3
        start_time = (9, 50)
        current_time = (9, 50)
        delay_updates = [
            (101, 2, 7)
        ]
        transfer_time = 3
        self.assertEqual(find_optimal_route(stops, routes, transfers, start_stop, end_stop, start_time, current_time, delay_updates, transfer_time), (10, 17))

if __name__ == '__main__':
    unittest.main()