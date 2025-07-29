import unittest
from supply_network import optimize_supply_network

class SupplyNetworkTest(unittest.TestCase):
    def test_basic_case(self):
        factories = [
            {"factory_id": "F1", "capacity": 100, "operating_cost": 500},
            {"factory_id": "F2", "capacity": 50, "operating_cost": 300},
        ]
        demand_centers = [
            {"demand_center_id": "D1", "demand": 70},
            {"demand_center_id": "D2", "demand": 80},
        ]
        transportation_costs = {
            ("F1", "D1"): 5,
            ("F1", "D2"): 7,
            ("F2", "D1"): 8,
            ("F2", "D2"): 4,
        }
        result = optimize_supply_network(factories, demand_centers, transportation_costs)
        self.assertIsNotNone(result)
        self.assertIn("factories", result)

        # Verify that each factory in the input is in the result and shipments do not exceed capacity.
        total_shipments = {dc["demand_center_id"]: 0 for dc in demand_centers}
        for factory in factories:
            fac_id = factory["factory_id"]
            self.assertIn(fac_id, result["factories"])
            fac_result = result["factories"][fac_id]
            shipments = fac_result.get("shipments", {})
            shipment_sum = sum(shipments.values())
            if fac_result.get("operational", False):
                self.assertLessEqual(shipment_sum, factory["capacity"])
            else:
                self.assertEqual(shipment_sum, 0)
            # Accumulate shipments for each demand center.
            for dc_id, qty in shipments.items():
                total_shipments[dc_id] += qty

        for dc in demand_centers:
            self.assertEqual(total_shipments[dc["demand_center_id"]], dc["demand"])

    def test_insufficient_capacity(self):
        # Total capacity less than total demand, should return None.
        factories = [
            {"factory_id": "F1", "capacity": 20, "operating_cost": 500},
        ]
        demand_centers = [
            {"demand_center_id": "D1", "demand": 30},
        ]
        transportation_costs = {
            ("F1", "D1"): 5,
        }
        result = optimize_supply_network(factories, demand_centers, transportation_costs)
        self.assertIsNone(result)

    def test_no_transportation_route(self):
        # Transportation route missing, no valid shipment possible.
        factories = [
            {"factory_id": "F1", "capacity": 100, "operating_cost": 500},
        ]
        demand_centers = [
            {"demand_center_id": "D1", "demand": 50},
        ]
        transportation_costs = {
            # No route provided for F1 -> D1, implying no transportation possibility.
        }
        result = optimize_supply_network(factories, demand_centers, transportation_costs)
        self.assertIsNone(result)

    def test_complex_case(self):
        # More complex scenario with multiple factories and demand centers.
        factories = [
            {"factory_id": "F1", "capacity": 150, "operating_cost": 400},
            {"factory_id": "F2", "capacity": 100, "operating_cost": 350},
            {"factory_id": "F3", "capacity": 200, "operating_cost": 700},
        ]
        demand_centers = [
            {"demand_center_id": "D1", "demand": 80},
            {"demand_center_id": "D2", "demand": 90},
            {"demand_center_id": "D3", "demand": 100},
        ]
        transportation_costs = {
            ("F1", "D1"): 2,
            ("F1", "D2"): 4,
            ("F1", "D3"): 6,
            ("F2", "D1"): 3,
            ("F2", "D3"): 2,
            ("F3", "D2"): 3,
            ("F3", "D3"): 1,
        }
        result = optimize_supply_network(factories, demand_centers, transportation_costs)
        self.assertIsNotNone(result)
        self.assertIn("factories", result)

        total_shipments = {dc["demand_center_id"]: 0 for dc in demand_centers}
        for factory in factories:
            fac_id = factory["factory_id"]
            self.assertIn(fac_id, result["factories"])
            fac_result = result["factories"][fac_id]
            shipments = fac_result.get("shipments", {})
            shipment_sum = sum(shipments.values())
            if fac_result.get("operational", False):
                self.assertLessEqual(shipment_sum, factory["capacity"])
            else:
                self.assertEqual(shipment_sum, 0)
            for dc_id, qty in shipments.items():
                total_shipments[dc_id] += qty

        for dc in demand_centers:
            self.assertEqual(total_shipments[dc["demand_center_id"]], dc["demand"])

if __name__ == "__main__":
    unittest.main()