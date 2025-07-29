import unittest
from train_scheduling import TrainScheduler

class TestTrainScheduling(unittest.TestCase):
    def setUp(self):
        # Create a fresh scheduler instance for each test
        self.scheduler = TrainScheduler(10000)  # Assuming constructor takes number of stations

    def test_single_track_shortest_time(self):
        # Add a simple track between station 0 and 1
        self.scheduler.add_track(0, 1, travel_time=10, capacity=50)
        # Verify shortest time should be direct travel_time
        self.assertEqual(self.scheduler.shortest_time(0, 1), 10)
        # For max_passengers, given time_window of 20: departures allowed = 20 - 10 + 1 = 11, total passengers = 11 * 50 = 550
        self.assertEqual(self.scheduler.max_passengers(0, 1, time_window=20), 550)

    def test_updated_track(self):
        # Add initial track and then update it
        self.scheduler.add_track(2, 3, travel_time=15, capacity=70)
        self.assertEqual(self.scheduler.shortest_time(2, 3), 15)
        self.assertEqual(self.scheduler.max_passengers(2, 3, time_window=25), (25 - 15 + 1) * 70)
        # Update the same track with new travel_time and capacity
        self.scheduler.add_track(2, 3, travel_time=12, capacity=90)
        self.assertEqual(self.scheduler.shortest_time(2, 3), 12)
        self.assertEqual(self.scheduler.max_passengers(2, 3, time_window=25), (25 - 12 + 1) * 90)

    def test_unreachable_station(self):
        # Without connecting tracks, stations 4 and 5 are disconnected.
        self.assertEqual(self.scheduler.shortest_time(4, 5), -1)
        self.assertEqual(self.scheduler.max_passengers(4, 5, time_window=50), 0)

    def test_multiple_routes_selects_optimal(self):
        # Construct a network with two distinct routes from 0 to 3.
        # Route A: 0 -> 1 -> 3: travel_time = 10+10=20, bottleneck capacity = min(100, 100) = 100.
        self.scheduler.add_track(0, 1, travel_time=10, capacity=100)
        self.scheduler.add_track(1, 3, travel_time=10, capacity=100)
        # Route B: 0 -> 2 -> 3: travel_time = 5+5=10, bottleneck capacity = min(50, 50) = 50.
        self.scheduler.add_track(0, 2, travel_time=5, capacity=50)
        self.scheduler.add_track(2, 3, travel_time=5, capacity=50)
        # The shortest_time should choose Route B since total time is 10.
        self.assertEqual(self.scheduler.shortest_time(0, 3), 10)
        # For time_window=30, departures for Route A: 30-20+1 = 11 departures, total = 1100; for Route B: 30-10+1 = 21 departures, total = 1050.
        # But note: maximum passengers is determined by selecting the route that yields higher throughput.
        # Therefore, optimal throughput is from Route A (despite being slower) with 1100 passengers.
        self.assertEqual(self.scheduler.max_passengers(0, 3, time_window=30), 1100)

    def test_time_window_edge_case(self):
        # Add a track and request max_passengers with time_window equal to travel time.
        self.scheduler.add_track(5, 6, travel_time=20, capacity=80)
        # Only one departure time is allowed when time_window equals travel_time.
        self.assertEqual(self.scheduler.shortest_time(5, 6), 20)
        self.assertEqual(self.scheduler.max_passengers(5, 6, time_window=20), 1 * 80)
        # If time_window is less than travel_time, the route is infeasible.
        self.assertEqual(self.scheduler.max_passengers(5, 6, time_window=15), 0)

    def test_complex_network(self):
        # Construct a more complex network
        # Stations: 0,1,2,3,4,5 with several interconnections.
        self.scheduler.add_track(0, 1, travel_time=8, capacity=120)
        self.scheduler.add_track(1, 2, travel_time=12, capacity=100)
        self.scheduler.add_track(0, 3, travel_time=15, capacity=80)
        self.scheduler.add_track(3, 2, travel_time=5, capacity=90)
        self.scheduler.add_track(2, 4, travel_time=10, capacity=110)
        self.scheduler.add_track(4, 5, travel_time=10, capacity=95)
        self.scheduler.add_track(3, 5, travel_time=25, capacity=60)
        # Check shortest time from 0 to 5
        # Possible path: 0-1-2-4-5: total time = 8+12+10+10 = 40, bottleneck = min(120,100,110,95)=95
        # Alternative: 0-3-5: total time =15+25=40, bottleneck = min(80,60)=60
        # Alternative: 0-3-2-4-5: total time = 15+5+10+10=40, bottleneck = min(80,90,110,95)=80
        self.assertEqual(self.scheduler.shortest_time(0, 5), 40)
        # For time_window of 50, calculate maximum departures and throughput for each route:
        # Route via 0-1-2-4-5: departures = 50 - 40 + 1 = 11, throughput = 11 * 95 = 1045
        # Route via 0-3-5: throughput = 11 * 60 = 660
        # Route via 0-3-2-4-5: throughput = 11 * 80 = 880
        # Thus, optimal throughput = 1045.
        self.assertEqual(self.scheduler.max_passengers(0, 5, time_window=50), 1045)

if __name__ == '__main__':
    unittest.main()