import unittest
from transit_routing import find_fastest_arrival

class TransitRoutingTest(unittest.TestCase):
    def test_direct_route_immediate_departure(self):
        # Direct route available with immediate departure.
        stations = [1, 2]
        routes = [(1, 2, 101, 10)]
        timetables = {101: [0, 10, 20]}
        start_station = 1
        destination_station = 2
        departure_time = 0
        disruptions = []
        # Expected: Depart at 0, arrive at 10.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), 10)

    def test_direct_route_waiting_for_next_departure(self):
        # Arrival requires waiting for the next available departure.
        stations = [1, 2]
        routes = [(1, 2, 101, 10)]
        timetables = {101: [5, 15, 25]}
        start_station = 1
        destination_station = 2
        departure_time = 0
        disruptions = []
        # Expected: Next departure is at 5, arrival at 15.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), 15)

    def test_direct_route_with_disruption(self):
        # Route is disrupted for initial departure so must take later departure.
        stations = [1, 2]
        routes = [(1, 2, 101, 10)]
        timetables = {101: [0, 10, 20]}
        start_station = 1
        destination_station = 2
        departure_time = 0
        # Disruption blocks route 101 from time 0 to 5.
        disruptions = [(101, 0, 5)]
        # Departure at 0 is blocked; next valid departure is at 10, arrival at 20.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), 20)

    def test_multi_hop_route(self):
        # Two routes with transfer, no disruptions.
        stations = [1, 2, 3]
        routes = [(1, 2, 101, 10), (2, 3, 102, 10)]
        timetables = {
            101: [0, 15, 30],
            102: [15, 30, 45]
        }
        start_station = 1
        destination_station = 3
        departure_time = 0
        disruptions = []
        # For route 101, depart at 0 arrive at 10 at station 2;
        # then wait until 15 on route 102 and arrive at 25.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), 25)

    def test_multiple_paths_with_disruption(self):
        # Two paths are available; one is disrupted forcing the algorithm to choose an alternative.
        stations = [1, 2, 3]
        routes = [
            (1, 2, 101, 10),
            (2, 3, 102, 10),
            (1, 3, 103, 25)
        ]
        timetables = {
            101: [0, 10, 20],
            102: [20, 30, 40],
            103: [5, 15, 30]
        }
        start_station = 1
        destination_station = 3
        departure_time = 0
        # Disruptions block route 102 entirely.
        disruptions = [(102, 0, 100)]
        # So the optimal path is via route 103; earliest departure at 5 and arrival at 5+25 = 30.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), 30)

    def test_wrap_around_midnight(self):
        # If no departure is available on the same day after the start time, use next day's timetable (timetable repeats).
        stations = [1, 2]
        routes = [(1, 2, 101, 10)]
        timetables = {101: [0, 100]}
        start_station = 1
        destination_station = 2
        departure_time = 110
        disruptions = []
        # Next available departure is timetable[0] on the next day, which is 0 + 1440 = 1440, so arrival = 1440+10=1450.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), 1450)

    def test_multiple_disruptions_on_same_route(self):
        # Test with multiple overlapping disruptions.
        stations = [1, 2]
        routes = [(1, 2, 101, 10)]
        timetables = {101: [0, 30, 60, 90]}
        start_station = 1
        destination_station = 2
        disruptions = [
            (101, 25, 20),  # Blocks time 25 to 45
            (101, 50, 20)   # Blocks time 50 to 70
        ]
        # Case 1: start at 0, can use departure at 0 (arrives at 10) since it is not disrupted.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, 0, disruptions
        ), 10)
        
        # Case 2: start at 20, departures: 30, 60, 90.
        # Departure at 30 is disrupted (falls in 25-45), 60 is disrupted (falls in 50-70), chosen next is 90 (arrives at 100).
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, 20, disruptions
        ), 100)

    def test_no_possible_route(self):
        # Test a scenario where no route can lead to the destination.
        stations = [1, 2, 3]
        routes = [(1, 2, 101, 10)]
        timetables = {101: [0, 10, 20]}
        start_station = 1
        destination_station = 3
        departure_time = 0
        disruptions = []
        # Since there is no path from station 1 to station 3, expect -1.
        self.assertEqual(find_fastest_arrival(
            stations, routes, timetables, start_station, destination_station, departure_time, disruptions
        ), -1)

if __name__ == '__main__':
    unittest.main()