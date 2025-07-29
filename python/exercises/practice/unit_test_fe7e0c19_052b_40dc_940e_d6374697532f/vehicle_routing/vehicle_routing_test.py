import unittest
from vehicle_routing import route_vehicles

class VehicleRoutingTest(unittest.TestCase):
    def setUp(self):
        # Sample network used for most tests.
        self.network = {
            "A": [{"to": "B", "travel_time": 10, "length": 100}, {"to": "C", "travel_time": 15, "length": 150}],
            "B": [{"to": "D", "travel_time": 20, "length": 200}],
            "C": [{"to": "D", "travel_time": 5, "length": 50}],
            "D": []
        }

    def validate_actions_structure(self, actions, valid_package_ids):
        # Ensure actions is a list of tuples with proper types.
        self.assertIsInstance(actions, list)
        for action in actions:
            self.assertEqual(len(action), 3)
            act_type, location, package_id = action
            self.assertIn(act_type, ["move", "pickup", "deliver"])
            self.assertIsInstance(location, str)
            if act_type == "move":
                self.assertIsNone(package_id)
            else:
                self.assertIsInstance(package_id, str)
                self.assertIn(package_id, valid_package_ids)

    def test_basic_routing(self):
        # Single vehicle, single package, no dynamic traffic updates.
        vehicles = [
            {"id": "V1", "location": "A", "capacity": 2, "remaining_time": 3600}
        ]
        packages = [
            {"id": "P1", "pickup_location": "B", "delivery_location": "D", "priority": 1, "sla_time": 600}
        ]
        dynamic_traffic_updates = []
        result = route_vehicles(self.network, vehicles, packages, dynamic_traffic_updates)

        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("V1", result)
        actions = result["V1"]
        self.assertGreater(len(actions), 0)
        valid_package_ids = {p["id"] for p in packages}
        self.validate_actions_structure(actions, valid_package_ids)

        # Ensure that there is one pickup and one deliver for package P1
        pickup_count = sum(1 for a in actions if a[0] == "pickup" and a[2] == "P1")
        deliver_count = sum(1 for a in actions if a[0] == "deliver" and a[2] == "P1")
        self.assertEqual(pickup_count, 1)
        self.assertEqual(deliver_count, 1)

    def test_dynamic_traffic_update(self):
        # Test if dynamic traffic updates are processed. We simulate changes on A->B and C->D.
        vehicles = [
            {"id": "V1", "location": "A", "capacity": 2, "remaining_time": 3600},
            {"id": "V2", "location": "C", "capacity": 1, "remaining_time": 1800}
        ]
        packages = [
            {"id": "P1", "pickup_location": "B", "delivery_location": "D", "priority": 1, "sla_time": 800},
            {"id": "P2", "pickup_location": "A", "delivery_location": "D", "priority": 2, "sla_time": 1200}
        ]
        # Update travel time for A->B and C->D
        dynamic_updates = [("A", "B", 12), ("C", "D", 8)]
        
        result = route_vehicles(self.network, vehicles, packages, dynamic_updates)
        self.assertIsInstance(result, dict)
        for vehicle in vehicles:
            self.assertIn(vehicle["id"], result)
            actions = result[vehicle["id"]]
            valid_package_ids = {p["id"] for p in packages}
            self.validate_actions_structure(actions, valid_package_ids)

    def test_vehicle_capacity(self):
        # Test scenario where vehicle capacity limits package pickups.
        vehicles = [
            {"id": "V1", "location": "A", "capacity": 1, "remaining_time": 3600}
        ]
        packages = [
            {"id": "P1", "pickup_location": "A", "delivery_location": "B", "priority": 2, "sla_time": 1000},
            {"id": "P2", "pickup_location": "A", "delivery_location": "C", "priority": 1, "sla_time": 1000}
        ]
        dynamic_traffic_updates = []
        result = route_vehicles(self.network, vehicles, packages, dynamic_traffic_updates)
        self.assertIn("V1", result)
        actions = result["V1"]
        # Count the number of pickup actions
        pickup_actions = [a for a in actions if a[0] == "pickup"]
        # The vehicle capacity is 1, so it should not pickup more than one package at a time.
        self.assertLessEqual(len(pickup_actions), 1)

    def test_remaining_time_limit(self):
        # Test scenario where vehicle has a limited remaining_time.
        vehicles = [
            {"id": "V1", "location": "A", "capacity": 2, "remaining_time": 30}  # Very short time
        ]
        packages = [
            {"id": "P1", "pickup_location": "B", "delivery_location": "D", "priority": 3, "sla_time": 100}
        ]
        dynamic_traffic_updates = []
        result = route_vehicles(self.network, vehicles, packages, dynamic_traffic_updates)
        self.assertIn("V1", result)
        actions = result["V1"]

        # Since remaining_time is very limited, it is possible that the vehicle cannot complete delivery.
        # We will check that if any actions are planned, then the first action should be a move, but the delivery
        # might not occur. Also, ensure that the actions list is not planning to pickup/deliver if not enough time.
        if actions:
            first_action = actions[0]
            self.assertEqual(first_action[0], "move")
            # Check that any pickup/deliver actions for P1 do not lead to two occurrences.
            pickup_count = sum(1 for a in actions if a[0] == "pickup" and a[2] == "P1")
            deliver_count = sum(1 for a in actions if a[0] == "deliver" and a[2] == "P1")
            self.assertLessEqual(pickup_count, 1)
            self.assertLessEqual(deliver_count, 1)

    def test_multiple_vehicle_multiple_packages(self):
        # Complex scenario with multiple vehicles and packages.
        vehicles = [
            {"id": "V1", "location": "A", "capacity": 2, "remaining_time": 3600},
            {"id": "V2", "location": "C", "capacity": 2, "remaining_time": 2400}
        ]
        packages = [
            {"id": "P1", "pickup_location": "B", "delivery_location": "D", "priority": 3, "sla_time": 900},
            {"id": "P2", "pickup_location": "A", "delivery_location": "C", "priority": 2, "sla_time": 1200},
            {"id": "P3", "pickup_location": "C", "delivery_location": "D", "priority": 1, "sla_time": 1500}
        ]
        dynamic_traffic_updates = [("B", "D", 25), ("A", "C", 16)]
        result = route_vehicles(self.network, vehicles, packages, dynamic_traffic_updates)
        self.assertIsInstance(result, dict)
        self.assertIn("V1", result)
        self.assertIn("V2", result)
        valid_package_ids = {p["id"] for p in packages}
        for vid in result:
            actions = result[vid]
            self.validate_actions_structure(actions, valid_package_ids)

        # Ensure that each package is picked up and delivered at most once by any vehicle.
        for pkg in packages:
            total_pickups = 0
            total_delivers = 0
            for actions in result.values():
                total_pickups += sum(1 for a in actions if a[0] == "pickup" and a[2] == pkg["id"])
                total_delivers += sum(1 for a in actions if a[0] == "deliver" and a[2] == pkg["id"])
            self.assertLessEqual(total_pickups, 1)
            self.assertLessEqual(total_delivers, 1)

if __name__ == "__main__":
    unittest.main()