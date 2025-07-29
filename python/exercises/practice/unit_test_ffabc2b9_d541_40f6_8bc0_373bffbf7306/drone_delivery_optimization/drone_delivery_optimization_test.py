import unittest
from drone_delivery_optimization import schedule_deliveries

class DroneDeliveryOptimizationTest(unittest.TestCase):

    def get_adjusted_flight_time(self, city_graph):
        def get_adjusted_flight_time(node1, node2, current_time):
            for edge in city_graph["edges"]:
                if (edge["from"] == node1 and edge["to"] == node2) or (edge["from"] == node2 and edge["to"] == node1):
                    return edge["weight"] + (current_time % 3)
            return 10**6
        return get_adjusted_flight_time

    def test_basic_scenario(self):
        city_graph = {
            "nodes": ["A", "B", "C", "D"],
            "edges": [
                {"from": "A", "to": "B", "weight": 5},
                {"from": "B", "to": "C", "weight": 5},
                {"from": "C", "to": "D", "weight": 5},
                {"from": "A", "to": "D", "weight": 20}
            ]
        }
        charging_stations = ["A", "D"]
        delivery_requests = [
            {"id": "r1", "origin": "A", "destination": "C", "weight": 1, "volume": 1, "time_window": (0, 30)},
            {"id": "r2", "origin": "B", "destination": "D", "weight": 1, "volume": 1, "time_window": (10, 40)},
            {"id": "r3", "origin": "C", "destination": "A", "weight": 1, "volume": 1, "time_window": (5, 35)}
        ]
        drones = [
            {"id": "d1", "current_location": "A", "capacity": {"weight": 2, "volume": 2}, "max_flight_time": 15},
            {"id": "d2", "current_location": "D", "capacity": {"weight": 2, "volume": 2}, "max_flight_time": 15}
        ]
        simulation_duration = 50
        get_time_func = self.get_adjusted_flight_time(city_graph)

        schedule = schedule_deliveries(city_graph, charging_stations, delivery_requests, drones, get_time_func, simulation_duration)
        
        # Verify that schedule is a dictionary with entries for each drone
        self.assertIsInstance(schedule, dict)
        for drone in drones:
            self.assertIn(drone["id"], schedule)
            events = schedule[drone["id"]]
            self.assertIsInstance(events, list)
            last_time = -1
            for event in events:
                self.assertIn("location", event)
                self.assertIn("arrival_time", event)
                self.assertIn("deliveries", event)
                # Ensure that the events are in chronological order
                self.assertGreaterEqual(event["arrival_time"], last_time)
                last_time = event["arrival_time"]
                # Ensure events occur within simulation time limits
                self.assertLessEqual(event["arrival_time"], simulation_duration)
                # Check time window constraints for each delivered request
                for delivery in event["deliveries"]:
                    req = next((req for req in delivery_requests if req["id"] == delivery), None)
                    self.assertIsNotNone(req)
                    start, end = req["time_window"]
                    self.assertGreaterEqual(event["arrival_time"], start)
                    self.assertLessEqual(event["arrival_time"], end)

    def test_impossible_delivery(self):
        city_graph = {
            "nodes": ["A", "B"],
            "edges": [
                {"from": "A", "to": "B", "weight": 50}
            ]
        }
        charging_stations = ["A"]
        delivery_requests = [
            {"id": "r1", "origin": "A", "destination": "B", "weight": 1, "volume": 1, "time_window": (0, 10)}
        ]
        drones = [
            {"id": "d1", "current_location": "A", "capacity": {"weight": 2, "volume": 2}, "max_flight_time": 15}
        ]
        simulation_duration = 20
        get_time_func = self.get_adjusted_flight_time(city_graph)

        schedule = schedule_deliveries(city_graph, charging_stations, delivery_requests, drones, get_time_func, simulation_duration)
        
        # Verify that the delivery request which is impossible to meet is not scheduled
        delivered_ids = []
        for events in schedule.values():
            for event in events:
                delivered_ids.extend(event["deliveries"])
        self.assertNotIn("r1", delivered_ids)

    def test_capacity_and_battery_constraints(self):
        city_graph = {
            "nodes": ["A", "B", "C"],
            "edges": [
                {"from": "A", "to": "B", "weight": 7},
                {"from": "B", "to": "C", "weight": 7},
                {"from": "C", "to": "A", "weight": 10}
            ]
        }
        charging_stations = ["A", "C"]
        delivery_requests = [
            {"id": "r1", "origin": "A", "destination": "B", "weight": 1, "volume": 1, "time_window": (0, 30)},
            {"id": "r2", "origin": "B", "destination": "C", "weight": 1, "volume": 1, "time_window": (5, 35)},
            {"id": "r3", "origin": "B", "destination": "A", "weight": 2, "volume": 2, "time_window": (10, 40)}
        ]
        drones = [
            {"id": "d1", "current_location": "A", "capacity": {"weight": 2, "volume": 2}, "max_flight_time": 14}
        ]
        simulation_duration = 50
        get_time_func = self.get_adjusted_flight_time(city_graph)

        schedule = schedule_deliveries(city_graph, charging_stations, delivery_requests, drones, get_time_func, simulation_duration)

        # Verify that the drone respects capacity constraints by checking if heavier requests are scheduled alone
        total_delivered = set()
        for event in schedule[drones[0]["id"]]:
            for delivery_id in event["deliveries"]:
                total_delivered.add(delivery_id)
        if "r3" in total_delivered:
            for event in schedule[drones[0]["id"]]:
                if "r3" in event["deliveries"]:
                    self.assertEqual(len(event["deliveries"]), 1)

    def test_simulation_duration_limit(self):
        city_graph = {
            "nodes": ["A", "B", "C", "D"],
            "edges": [
                {"from": "A", "to": "B", "weight": 3},
                {"from": "B", "to": "C", "weight": 3},
                {"from": "C", "to": "D", "weight": 3},
                {"from": "D", "to": "A", "weight": 12}
            ]
        }
        charging_stations = ["A", "D"]
        delivery_requests = [
            {"id": "r1", "origin": "A", "destination": "D", "weight": 1, "volume": 1, "time_window": (0, 15)},
            {"id": "r2", "origin": "B", "destination": "C", "weight": 1, "volume": 1, "time_window": (5, 20)},
            {"id": "r3", "origin": "C", "destination": "A", "weight": 1, "volume": 1, "time_window": (10, 25)}
        ]
        drones = [
            {"id": "d1", "current_location": "A", "capacity": {"weight": 3, "volume": 3}, "max_flight_time": 20}
        ]
        simulation_duration = 25
        get_time_func = self.get_adjusted_flight_time(city_graph)

        schedule = schedule_deliveries(city_graph, charging_stations, delivery_requests, drones, get_time_func, simulation_duration)

        # Verify that no event in the schedule exceeds the simulation duration
        for event in schedule[drones[0]["id"]]:
            self.assertLessEqual(event["arrival_time"], simulation_duration)

if __name__ == '__main__':
    unittest.main()