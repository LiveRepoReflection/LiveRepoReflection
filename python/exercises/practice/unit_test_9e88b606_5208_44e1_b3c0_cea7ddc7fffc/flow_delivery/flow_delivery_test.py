import unittest
from datetime import timedelta
from flow_delivery import optimize_delivery

class TestFlowDelivery(unittest.TestCase):
    def test_single_commodity_valid(self):
        # Setup a simple network with one commodity
        network = [
            {"start_node": "A", "end_node": "B", "capacity": 2, "travel_time": 5},
            {"start_node": "B", "end_node": "C", "capacity": 1, "travel_time": 10},
            {"start_node": "A", "end_node": "C", "capacity": 1, "travel_time": 15},
        ]
        commodities = [
            {
                "commodity_id": "c1",
                "source": "A",
                "destination": "C",
                "demand": 2,
                "start_time": 0,
                "end_time": 30
            }
        ]
        # Execute optimization
        schedule = optimize_delivery(network, commodities)
        
        # Validate that schedule has result for commodity c1 and exactly two deliveries
        self.assertIn("c1", schedule)
        self.assertEqual(len(schedule["c1"]), 2)
        
        # Validate each truck's delivery schedule
        for delivery in schedule["c1"]:
            self.assertIsInstance(delivery, dict)
            self.assertIn("route", delivery)
            self.assertIn("departure_time", delivery)
            # Check route starts at source and ends at destination
            self.assertEqual(delivery["route"][0], "A")
            self.assertEqual(delivery["route"][-1], "C")
            # Check departure time is within the valid time window
            self.assertGreaterEqual(delivery["departure_time"], 0)
            # Compute estimated arrival time based on travel times along route
            travel_time = 0
            route = delivery["route"]
            for i in range(len(route) - 1):
                for edge in network:
                    if edge["start_node"] == route[i] and edge["end_node"] == route[i+1]:
                        travel_time += edge["travel_time"]
                        break
            arrival_time = delivery["departure_time"] + travel_time
            self.assertLessEqual(arrival_time, 30)
    
    def test_multi_commodity_valid(self):
        # Setup a network with multiple commodities
        network = [
            {"start_node": "W", "end_node": "X", "capacity": 3, "travel_time": 4},
            {"start_node": "X", "end_node": "Y", "capacity": 2, "travel_time": 6},
            {"start_node": "W", "end_node": "Z", "capacity": 1, "travel_time": 10},
            {"start_node": "Z", "end_node": "Y", "capacity": 2, "travel_time": 5},
        ]
        commodities = [
            {
                "commodity_id": "c1",
                "source": "W",
                "destination": "Y",
                "demand": 2,
                "start_time": 0,
                "end_time": 20
            },
            {
                "commodity_id": "c2",
                "source": "W",
                "destination": "Y",
                "demand": 1,
                "start_time": 5,
                "end_time": 25
            }
        ]
        schedule = optimize_delivery(network, commodities)
        
        # Check that both commodities have schedules matching their demands
        for commodity in commodities:
            cid = commodity["commodity_id"]
            self.assertIn(cid, schedule)
            self.assertEqual(len(schedule[cid]), commodity["demand"])
            for delivery in schedule[cid]:
                self.assertEqual(delivery["route"][0], commodity["source"])
                self.assertEqual(delivery["route"][-1], commodity["destination"])
                self.assertGreaterEqual(delivery["departure_time"], commodity["start_time"])
                # Calculate total travel time along the route
                travel_time = 0
                route = delivery["route"]
                for i in range(len(route) - 1):
                    found = False
                    for edge in network:
                        if edge["start_node"] == route[i] and edge["end_node"] == route[i+1]:
                            travel_time += edge["travel_time"]
                            found = True
                            break
                    self.assertTrue(found, "Edge not found in network")
                arrival_time = delivery["departure_time"] + travel_time
                self.assertLessEqual(arrival_time, commodity["end_time"])
    
    def test_source_equals_destination(self):
        # Test case where commodity source and destination are the same
        network = [
            {"start_node": "P", "end_node": "Q", "capacity": 2, "travel_time": 7}
        ]
        commodities = [
            {
                "commodity_id": "c_same",
                "source": "P",
                "destination": "P",
                "demand": 3,
                "start_time": 10,
                "end_time": 10
            }
        ]
        schedule = optimize_delivery(network, commodities)
        # For same source and destination, we expect no travel needed.
        self.assertIn("c_same", schedule)
        self.assertEqual(len(schedule["c_same"]), 3)
        for delivery in schedule["c_same"]:
            self.assertEqual(delivery["route"], ["P"])
            # Departure time might be set to start_time since no travel is needed.
            self.assertEqual(delivery["departure_time"], 10)
    
    def test_no_feasible_solution(self):
        # Setup a scenario where the demand cannot be met due to capacity/time constraints.
        network = [
            {"start_node": "M", "end_node": "N", "capacity": 1, "travel_time": 10}
        ]
        commodities = [
            {
                "commodity_id": "c_fail",
                "source": "M",
                "destination": "N",
                "demand": 3,
                "start_time": 0,
                "end_time": 15
            }
        ]
        with self.assertRaises(Exception):
            optimize_delivery(network, commodities)

if __name__ == "__main__":
    unittest.main()