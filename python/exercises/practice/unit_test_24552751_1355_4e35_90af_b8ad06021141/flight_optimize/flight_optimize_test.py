import unittest
from flight_optimize import optimize_flight_paths

class FlightOptimizeTest(unittest.TestCase):

    def test_same_location(self):
        graph = [
            {"source": "A", "destination": "B", "base_cost": 50, "base_time": 60}
        ]
        aircraft_list = [
            {"aircraft_id": "AC1", "current_location": "A", "destination": "A", "departure_time": 100}
        ]
        events = []
        penalty_per_minute = 10
        result = optimize_flight_paths(graph, aircraft_list, events, penalty_per_minute)
        expected = [
            {
                "aircraft_id": "AC1",
                "path": ["A"],
                "total_cost": 0,
                "total_time": 0,
                "departure_delay": 0
            }
        ]
        self.assertEqual(result, expected)

    def test_no_path(self):
        graph = [
            {"source": "A", "destination": "B", "base_cost": 50, "base_time": 60},
            {"source": "B", "destination": "C", "base_cost": 70, "base_time": 80}
        ]
        aircraft_list = [
            {"aircraft_id": "AC2", "current_location": "A", "destination": "D", "departure_time": 30}
        ]
        events = []
        penalty_per_minute = 10
        result = optimize_flight_paths(graph, aircraft_list, events, penalty_per_minute)
        expected = [
            {
                "aircraft_id": "AC2",
                "path": [],
                "total_cost": 0,
                "total_time": 0,
                "departure_delay": 0
            }
        ]
        self.assertEqual(result, expected)

    def test_complex_events(self):
        graph = [
            {"source": "A", "destination": "B", "base_cost": 50, "base_time": 60},
            {"source": "B", "destination": "C", "base_cost": 70, "base_time": 80},
            {"source": "A", "destination": "C", "base_cost": 150, "base_time": 100},
            {"source": "B", "destination": "D", "base_cost": 40, "base_time": 50},
            {"source": "C", "destination": "D", "base_cost": 30, "base_time": 40}
        ]
        aircraft_list = [
            {"aircraft_id": "AC1", "current_location": "A", "destination": "D", "departure_time": 10},
            {"aircraft_id": "AC2", "current_location": "B", "destination": "D", "departure_time": 15}
        ]
        events = [
            {"type": "WeatherDelay", "airport_code": "A", "delay_time": 20},
            {"type": "IncreasedDemand", "source": "B", "destination": "C", "cost_increase": 30, "time_increase": 10},
            {"type": "FuelPriceChange", "price_change_percentage": 0.1},
            {"type": "RouteClosure", "source": "A", "destination": "C"}
        ]
        penalty_per_minute = 10
        result = optimize_flight_paths(graph, aircraft_list, events, penalty_per_minute)
        expected = [
            {
                "aircraft_id": "AC1",
                "path": ["A", "B", "D"],
                "total_cost": 99,  # Computed as: (50*1.1=55) + (40*1.1=44) = 99
                "total_time": 110, # Computed as: 60 + 50 = 110
                "departure_delay": 20
            },
            {
                "aircraft_id": "AC2",
                "path": ["B", "D"],
                "total_cost": 44,  # Computed as: 40*1.1 = 44
                "total_time": 50,
                "departure_delay": 0
            }
        ]
        self.assertEqual(result, expected)

    def test_conflicting_events(self):
        graph = [
            {"source": "X", "destination": "Y", "base_cost": 100, "base_time": 120}
        ]
        aircraft_list = [
            {"aircraft_id": "AC3", "current_location": "X", "destination": "Y", "departure_time": 50}
        ]
        events = [
            {"type": "IncreasedDemand", "source": "X", "destination": "Y", "cost_increase": 50, "time_increase": 20},
            {"type": "RouteClosure", "source": "X", "destination": "Y"}
        ]
        penalty_per_minute = 10
        result = optimize_flight_paths(graph, aircraft_list, events, penalty_per_minute)
        expected = [
            {
                "aircraft_id": "AC3",
                "path": [],
                "total_cost": 0,
                "total_time": 0,
                "departure_delay": 0
            }
        ]
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()