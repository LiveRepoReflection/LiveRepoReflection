import unittest
from galactic_travel import find_earliest_arrival

class GalacticTravelTest(unittest.TestCase):
    def test_basic_path(self):
        # Basic valid path using the provided sample scenario.
        wormhole_network = {
            "Earth": {
                "StationAlpha": [
                    {"capacity": 10, "schedule": [(0, 100, 10)]},
                    {"capacity": 5, "schedule": [(0, 50, 15), (51, 100, 20)]}
                ]
            },
            "StationAlpha": {
                "Mars": [
                    {"capacity": 20, "schedule": [(0, 100, 30)]}
                ]
            },
            "Mars": {}
        }
        start_planet = "Earth"
        departure_time_window = (0, 50)
        destination_planet = "Mars"
        num_travelers = 7
        # Expected: Depart Earth at time 0 using the first wormhole: arrival at StationAlpha = 0+10 = 10.
        # Then depart immediately from StationAlpha to Mars: arrival = 10+30 = 40.
        expected = 40
        result = find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network)
        self.assertEqual(result, expected)

    def test_no_possible_path(self):
        # There is no outgoing wormhole from the start planet.
        wormhole_network = {
            "Earth": {},
            "Mars": {}
        }
        start_planet = "Earth"
        departure_time_window = (0, 100)
        destination_planet = "Mars"
        num_travelers = 1
        expected = None
        result = find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network)
        self.assertIsNone(result)

    def test_capacity_issue(self):
        # The only available wormhole does not have sufficient capacity.
        wormhole_network = {
            "Earth": {
                "Mars": [
                    {"capacity": 10, "schedule": [(0, 100, 20)]}
                ]
            },
            "Mars": {}
        }
        start_planet = "Earth"
        departure_time_window = (0, 50)
        destination_planet = "Mars"
        num_travelers = 15  # Exceeds capacity of 10.
        expected = None
        result = find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network)
        self.assertIsNone(result)

    def test_cycle(self):
        # The network contains a cycle. The algorithm must avoid infinite loops and pick the optimal path.
        wormhole_network = {
            "A": {
                "B": [
                    {"capacity": 10, "schedule": [(0, 100, 10)]}
                ]
            },
            "B": {
                "C": [
                    {"capacity": 10, "schedule": [(0, 100, 10)]}
                ]
            },
            "C": {
                "A": [
                    {"capacity": 10, "schedule": [(10, 100, 5)]}
                ],
                "Mars": [
                    {"capacity": 10, "schedule": [(0, 100, 30)]}
                ]
            },
            "Mars": {}
        }
        start_planet = "A"
        departure_time_window = (0, 50)
        destination_planet = "Mars"
        num_travelers = 5
        # A -> B: depart at 0, arrival at 10.
        # B -> C: depart at 10, arrival at 20.
        # C -> Mars: depart at 20, arrival at 20+30 = 50.
        expected = 50
        result = find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network)
        self.assertEqual(result, expected)

    def test_departure_window_edge(self):
        # Test departure at an edge value of schedule windows.
        wormhole_network = {
            "Earth": {
                "Moon": [
                    {"capacity": 5, "schedule": [(10, 10, 5)]}
                ]
            },
            "Moon": {
                "Mars": [
                    {"capacity": 5, "schedule": [(15, 15, 20)]}
                ]
            },
            "Mars": {}
        }
        start_planet = "Earth"
        departure_time_window = (10, 10)
        destination_planet = "Mars"
        num_travelers = 3
        # Depart exactly at 10 from Earth -> arrival Moon = 10+5 = 15.
        # Depart exactly at 15 from Moon -> arrival Mars = 15+20 = 35.
        expected = 35
        result = find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        # Multiple routes exist, and the optimal (earliest arrival) path should be chosen.
        wormhole_network = {
            "Earth": {
                "Alpha": [
                    {"capacity": 10, "schedule": [(0, 100, 50)]}
                ],
                "Beta": [
                    {"capacity": 10, "schedule": [(0, 100, 30)]}
                ]
            },
            "Alpha": {
                "Mars": [
                    {"capacity": 10, "schedule": [(0, 100, 10)]}
                ]
            },
            "Beta": {
                "Mars": [
                    {"capacity": 10, "schedule": [(0, 100, 50)]}
                ]
            },
            "Mars": {}
        }
        start_planet = "Earth"
        departure_time_window = (0, 50)
        destination_planet = "Mars"
        num_travelers = 5
        # Two possible paths:
        # Path 1: Earth -> Alpha -> Mars:
        #   Depart at 0 from Earth: arrival at Alpha = 0+50 = 50.
        #   Depart at 50 from Alpha: arrival at Mars = 50+10 = 60.
        # Path 2: Earth -> Beta -> Mars:
        #   Depart at 0 from Earth: arrival at Beta = 0+30 = 30.
        #   Depart at 30 from Beta: arrival at Mars = 30+50 = 80.
        # The optimal arrival is 60.
        expected = 60
        result = find_earliest_arrival(start_planet, departure_time_window, destination_planet, num_travelers, wormhole_network)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()