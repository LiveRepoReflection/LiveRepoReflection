import unittest
from logistics_network import optimize_network

class TestLogisticsNetwork(unittest.TestCase):
    def test_basic_case(self):
        DCs = [
            {"id": 1, "location": (0, 0), "capacity": 100, "fixed_cost": 500},
            {"id": 2, "location": (10, 10), "capacity": 150, "fixed_cost": 700}
        ]
        customers = [
            {"id": 101, "location": (2, 3), "demand": 20},
            {"id": 102, "location": (5, 5), "demand": 30},
            {"id": 103, "location": (12, 8), "demand": 25}
        ]
        trucks = [
            {"id": 1, "capacity": 50, "cost_per_km": 2.5},
            {"id": 2, "capacity": 30, "cost_per_km": 1.8}
        ]
        SLA = 0.5  # 30 minutes
        max_trucks = 5
        
        result = optimize_network(DCs, customers, trucks, SLA, max_trucks)
        self.assertIsInstance(result, dict)
        self.assertIn("total_cost", result)
        self.assertIn("routes", result)
        self.assertTrue(len(result["routes"]) > 0)

    def test_insufficient_capacity(self):
        DCs = [
            {"id": 1, "location": (0, 0), "capacity": 10, "fixed_cost": 500}
        ]
        customers = [
            {"id": 101, "location": (2, 3), "demand": 20}
        ]
        trucks = [
            {"id": 1, "capacity": 50, "cost_per_km": 2.5}
        ]
        SLA = 0.5
        max_trucks = 5
        
        result = optimize_network(DCs, customers, trucks, SLA, max_trucks)
        self.assertEqual(result["total_cost"], -1)
        self.assertEqual(len(result["routes"]), 0)

    def test_sla_violation(self):
        DCs = [
            {"id": 1, "location": (0, 0), "capacity": 100, "fixed_cost": 500}
        ]
        customers = [
            {"id": 101, "location": (100, 100), "demand": 20}
        ]
        trucks = [
            {"id": 1, "capacity": 50, "cost_per_km": 2.5}
        ]
        SLA = 0.5  # 30 minutes (~141 km would take ~2.35 hours)
        max_trucks = 5
        
        result = optimize_network(DCs, customers, trucks, SLA, max_trucks)
        self.assertEqual(result["total_cost"], -1)
        self.assertEqual(len(result["routes"]), 0)

    def test_multiple_truck_types(self):
        DCs = [
            {"id": 1, "location": (0, 0), "capacity": 200, "fixed_cost": 500}
        ]
        customers = [
            {"id": 101, "location": (5, 5), "demand": 45},
            {"id": 102, "location": (6, 6), "demand": 30}
        ]
        trucks = [
            {"id": 1, "capacity": 50, "cost_per_km": 2.5},
            {"id": 2, "capacity": 30, "cost_per_km": 1.8}
        ]
        SLA = 1.0
        max_trucks = 5
        
        result = optimize_network(DCs, customers, trucks, SLA, max_trucks)
        self.assertGreater(result["total_cost"], 0)
        self.assertEqual(len(result["routes"]), 2)

    def test_empty_inputs(self):
        result = optimize_network([], [], [], 0.5, 5)
        self.assertEqual(result["total_cost"], -1)
        self.assertEqual(len(result["routes"]), 0)

if __name__ == "__main__":
    unittest.main()