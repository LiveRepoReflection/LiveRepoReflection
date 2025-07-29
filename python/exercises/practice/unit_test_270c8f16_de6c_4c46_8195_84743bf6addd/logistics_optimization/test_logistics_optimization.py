import unittest
from logistics_optimization import optimize_logistics

class TestLogisticsOptimization(unittest.TestCase):
    def test_simple_feasible_case(self):
        warehouses = [1, 2, 3]
        routes = [
            {"source": 1, "destination": 2, "capacity": 100, "cost_per_unit": 1.0, "transport_time": 2.0},
            {"source": 2, "destination": 3, "capacity": 80, "cost_per_unit": 1.5, "transport_time": 3.0},
            {"source": 1, "destination": 3, "capacity": 50, "cost_per_unit": 2.0, "transport_time": 5.0},
        ]
        demands = [
            {"source": 1, "destination": 3, "quantity": 70, "deadline": 8.0},
        ]
        result = optimize_logistics(warehouses, routes, demands)
        self.assertNotEqual(result, "Infeasible")
        self.assertIsInstance(result, tuple)
        plan, cost = result
        self.assertIsInstance(plan, dict)
        self.assertIsInstance(cost, float)

    def test_infeasible_deadline(self):
        warehouses = [1, 2, 3]
        routes = [
            {"source": 1, "destination": 2, "capacity": 100, "cost_per_unit": 1.0, "transport_time": 2.0},
            {"source": 2, "destination": 3, "capacity": 80, "cost_per_unit": 1.5, "transport_time": 3.0},
        ]
        demands = [
            {"source": 1, "destination": 3, "quantity": 70, "deadline": 4.0},
        ]
        result = optimize_logistics(warehouses, routes, demands)
        self.assertEqual(result, "Infeasible")

    def test_capacity_constraint(self):
        warehouses = [1, 2, 3]
        routes = [
            {"source": 1, "destination": 2, "capacity": 50, "cost_per_unit": 1.0, "transport_time": 2.0},
            {"source": 2, "destination": 3, "capacity": 50, "cost_per_unit": 1.5, "transport_time": 3.0},
            {"source": 1, "destination": 3, "capacity": 10, "cost_per_unit": 2.0, "transport_time": 5.0},
        ]
        demands = [
            {"source": 1, "destination": 3, "quantity": 70, "deadline": 8.0},
        ]
        result = optimize_logistics(warehouses, routes, demands)
        self.assertEqual(result, "Infeasible")

    def test_multiple_demands(self):
        warehouses = [1, 2, 3, 4]
        routes = [
            {"source": 1, "destination": 2, "capacity": 100, "cost_per_unit": 1.0, "transport_time": 2.0},
            {"source": 2, "destination": 3, "capacity": 80, "cost_per_unit": 1.5, "transport_time": 3.0},
            {"source": 1, "destination": 3, "capacity": 50, "cost_per_unit": 2.0, "transport_time": 5.0},
            {"source": 3, "destination": 4, "capacity": 60, "cost_per_unit": 1.0, "transport_time": 2.0},
        ]
        demands = [
            {"source": 1, "destination": 3, "quantity": 70, "deadline": 8.0},
            {"source": 3, "destination": 4, "quantity": 30, "deadline": 5.0},
        ]
        result = optimize_logistics(warehouses, routes, demands)
        self.assertNotEqual(result, "Infeasible")
        plan, cost = result
        self.assertGreaterEqual(plan.get((3, 4), 0), 30)

    def test_cycle_handling(self):
        warehouses = [1, 2, 3, 4]
        routes = [
            {"source": 1, "destination": 2, "capacity": 100, "cost_per_unit": 1.0, "transport_time": 2.0},
            {"source": 2, "destination": 3, "capacity": 80, "cost_per_unit": 1.5, "transport_time": 3.0},
            {"source": 3, "destination": 1, "capacity": 50, "cost_per_unit": 0.5, "transport_time": 1.0},
            {"source": 1, "destination": 4, "capacity": 60, "cost_per_unit": 2.0, "transport_time": 4.0},
        ]
        demands = [
            {"source": 1, "destination": 4, "quantity": 50, "deadline": 10.0},
        ]
        result = optimize_logistics(warehouses, routes, demands)
        self.assertNotEqual(result, "Infeasible")

    def test_large_quantity(self):
        warehouses = [1, 2, 3]
        routes = [
            {"source": 1, "destination": 2, "capacity": 1000, "cost_per_unit": 1.0, "transport_time": 2.0},
            {"source": 2, "destination": 3, "capacity": 800, "cost_per_unit": 1.5, "transport_time": 3.0},
            {"source": 1, "destination": 3, "capacity": 500, "cost_per_unit": 2.0, "transport_time": 5.0},
        ]
        demands = [
            {"source": 1, "destination": 3, "quantity": 1200, "deadline": 8.0},
        ]
        result = optimize_logistics(warehouses, routes, demands)
        self.assertNotEqual(result, "Infeasible")
        plan, cost = result
        total_shipped = sum(plan.values())
        self.assertGreaterEqual(total_shipped, 1200)

if __name__ == '__main__':
    unittest.main()