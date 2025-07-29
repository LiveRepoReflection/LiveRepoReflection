import unittest
from ride_match import maximize_matches

class RideMatchTest(unittest.TestCase):
    def test_basic_example(self):
        city_graph = {
            1: [(2, 5), (3, 10)],
            2: [(1, 5), (4, 7)],
            3: [(1, 10), (5, 3)],
            4: [(2, 7), (6, 2)],
            5: [(3, 3), (6, 8)],
            6: [(4, 2), (5, 8)]
        }
        ride_requests = [(101, 1, 6), (102, 2, 5)]
        driver_availabilities = [(201, 3), (202, 4)]
        communication_radius = 8
        max_ride_time = 20
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        self.assertIsInstance(matches, list)
        # Check that all matches are valid tuples
        for match in matches:
            self.assertIsInstance(match, tuple)
            self.assertEqual(len(match), 2)
            # Each match should contain a driver_id and rider_id
            driver_id, rider_id = match
            # Check that the driver and rider IDs are in the given lists
            driver_exists = any(d[0] == driver_id for d in driver_availabilities)
            rider_exists = any(r[0] == rider_id for r in ride_requests)
            self.assertTrue(driver_exists, f"Driver {driver_id} not in driver_availabilities")
            self.assertTrue(rider_exists, f"Rider {rider_id} not in ride_requests")
            
        # Each driver and rider should be matched at most once
        matched_drivers = [match[0] for match in matches]
        matched_riders = [match[1] for match in matches]
        self.assertEqual(len(matched_drivers), len(set(matched_drivers)), "Some drivers are matched multiple times")
        self.assertEqual(len(matched_riders), len(set(matched_riders)), "Some riders are matched multiple times")
        
        # One possible valid output is [(202, 102)]
        if matches:
            self.assertIn((202, 102), matches)
            
    def test_no_riders(self):
        city_graph = {
            1: [(2, 5)],
            2: [(1, 5)]
        }
        ride_requests = []
        driver_availabilities = [(201, 1)]
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, 5, 10)
        self.assertEqual(matches, [])
        
    def test_no_drivers(self):
        city_graph = {
            1: [(2, 5)],
            2: [(1, 5)]
        }
        ride_requests = [(101, 1, 2)]
        driver_availabilities = []
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, 5, 10)
        self.assertEqual(matches, [])
        
    def test_disconnected_graph(self):
        # Two disconnected components
        city_graph = {
            1: [(2, 5)],
            2: [(1, 5)],
            3: [(4, 3)],
            4: [(3, 3)]
        }
        ride_requests = [(101, 1, 2), (102, 3, 4)]
        driver_availabilities = [(201, 1), (202, 3)]
        communication_radius = 5
        max_ride_time = 10
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        # Expecting both rides to be matched
        self.assertEqual(len(matches), 2)
        
    def test_same_location_for_rider_and_driver(self):
        city_graph = {
            1: [(2, 5)],
            2: [(1, 5)]
        }
        ride_requests = [(101, 1, 2)]
        driver_availabilities = [(201, 1)]
        communication_radius = 1
        max_ride_time = 10
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        self.assertEqual(matches, [(201, 101)])
        
    def test_multiple_possible_matches_for_driver(self):
        city_graph = {
            1: [(2, 3), (3, 4)],
            2: [(1, 3), (3, 2)],
            3: [(1, 4), (2, 2)]
        }
        ride_requests = [(101, 1, 3), (102, 2, 3)]
        driver_availabilities = [(201, 1)]
        communication_radius = 5
        max_ride_time = 10
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0] in [(201, 101), (201, 102)])
        
    def test_multiple_drivers_one_rider(self):
        city_graph = {
            1: [(2, 3)],
            2: [(1, 3)]
        }
        ride_requests = [(101, 1, 2)]
        driver_availabilities = [(201, 1), (202, 1)]
        communication_radius = 5
        max_ride_time = 10
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0] in [(201, 101), (202, 101)])
        
    def test_complex_matching_scenario(self):
        city_graph = {
            1: [(2, 5), (4, 10)],
            2: [(1, 5), (3, 3), (5, 7)],
            3: [(2, 3), (6, 8)],
            4: [(1, 10), (5, 2)],
            5: [(2, 7), (4, 2), (6, 4)],
            6: [(3, 8), (5, 4)]
        }
        ride_requests = [
            (101, 1, 6),  # From 1 to 6
            (102, 2, 5),  # From 2 to 5
            (103, 3, 4),  # From 3 to 4
            (104, 4, 3)   # From 4 to 3
        ]
        driver_availabilities = [
            (201, 1),  # At location 1
            (202, 2),  # At location 2
            (203, 5)   # At location 5
        ]
        communication_radius = 10
        max_ride_time = 15
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        # Check that we have at most 3 matches (since there are 3 drivers)
        self.assertLessEqual(len(matches), 3)
        # Each driver and rider should be matched at most once
        matched_drivers = [match[0] for match in matches]
        matched_riders = [match[1] for match in matches]
        self.assertEqual(len(matched_drivers), len(set(matched_drivers)))
        self.assertEqual(len(matched_riders), len(set(matched_riders)))
        
    def test_zero_communication_radius(self):
        city_graph = {
            1: [(2, 5)],
            2: [(1, 5)]
        }
        ride_requests = [(101, 1, 2)]
        driver_availabilities = [(201, 1)]  # Driver at same location as rider
        communication_radius = 0
        max_ride_time = 10
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        self.assertEqual(matches, [(201, 101)])
        
    def test_zero_max_ride_time(self):
        city_graph = {
            1: [(2, 5)],
            2: [(1, 5)]
        }
        ride_requests = [(101, 1, 1)]  # Start and end at same location
        driver_availabilities = [(201, 1)]
        communication_radius = 5
        max_ride_time = 0
        
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        self.assertEqual(matches, [(201, 101)])
        
    def test_large_graph_efficiency(self):
        # Create a line graph with 1000 nodes
        city_graph = {}
        for i in range(1, 1000):
            if i == 1:
                city_graph[i] = [(i+1, 1)]
            elif i == 999:
                city_graph[i] = [(i-1, 1)]
            else:
                city_graph[i] = [(i-1, 1), (i+1, 1)]
        
        # 10 riders at different locations
        ride_requests = [(100+i, i*100, i*100+50) for i in range(1, 11)]
        # 5 drivers at different locations
        driver_availabilities = [(200+i, i*200) for i in range(1, 6)]
        communication_radius = 100
        max_ride_time = 200
        
        # This should execute quickly despite the large graph
        import time
        start_time = time.time()
        matches = maximize_matches(city_graph, ride_requests, driver_availabilities, communication_radius, max_ride_time)
        execution_time = time.time() - start_time
        
        # The test simply asserts that the function returns a valid result
        # within a reasonable time frame (10 seconds)
        self.assertLessEqual(execution_time, 10.0, "Algorithm is too slow for large graphs")
        self.assertIsInstance(matches, list)
        self.assertLessEqual(len(matches), min(len(ride_requests), len(driver_availabilities)))

if __name__ == "__main__":
    unittest.main()