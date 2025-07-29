import unittest
import math

from supply_chain_design import optimize_supply_chain

class TestSupplyChainDesign(unittest.TestCase):
    def test_simple_direct(self):
        # Scenario: One factory, no warehouse, one customer.
        factories = [{
            "location_id": "F1",
            "production_capacity": 100,
            "production_cost_per_unit": 1.0,
            "fixed_cost": 50.0
        }]
        
        warehouses = []
        
        customer_demand = [{
            "location_id": "C1",
            "demand": 50
        }]
        
        transportation_costs = {
            "F1": {"C1": 2.0},
            "C1": {}  # Customers do not ship further.
        }
        
        # Expected:
        # Production: 50 units at cost 1.0 = 50
        # Fixed factory cost = 50
        # Transportation: 50 units at cost 2.0 = 100
        # Total cost = 50 + 50 + 100 = 200
        expected = {
            "selected_factories": ["F1"],
            "selected_warehouses": [],
            "flow": {("F1", "C1"): 50},
            "total_cost": 200.0
        }
        
        result = optimize_supply_chain(factories, warehouses, customer_demand, transportation_costs)
        self.assertEqual(result["selected_factories"], expected["selected_factories"])
        self.assertEqual(result["selected_warehouses"], expected["selected_warehouses"])
        self.assertEqual(result["flow"], expected["flow"])
        self.assertAlmostEqual(result["total_cost"], expected["total_cost"], places=5)

    def test_with_warehouse(self):
        # Scenario: One factory, one warehouse, one customer.
        factories = [{
            "location_id": "F1",
            "production_capacity": 100,
            "production_cost_per_unit": 1.0,
            "fixed_cost": 50.0
        }]
        
        warehouses = [{
            "location_id": "W1",
            "storage_capacity": 100,
            "storage_cost_per_unit": 0.5,
            "fixed_cost": 30.0
        }]
        
        customer_demand = [{
            "location_id": "C1",
            "demand": 50
        }]
        
        # Transportation costs:
        # F1 -> W1: 0.5; W1 -> C1: 0.5; Direct F1 -> C1: 2.0.
        transportation_costs = {
            "F1": {"W1": 0.5, "C1": 2.0},
            "W1": {"C1": 0.5},
            "C1": {}
        }
        
        # Expected optimal path is to send F1->W1->C1.
        # Cost breakdown:
        # Factory fixed: 50; Warehouse fixed: 30.
        # Production cost: 1.0 * 50 = 50.
        # Transportation: F1->W1: 0.5 * 50 = 25; W1->C1: 0.5 * 50 = 25.
        # Warehouse storage cost: 0.5 * 50 = 25.
        # Total: 50 + 30 + 50 + 25 + 25 + 25 = 205.
        expected = {
            "selected_factories": ["F1"],
            "selected_warehouses": ["W1"],
            "flow": {("F1", "W1"): 50, ("W1", "C1"): 50},
            "total_cost": 205.0
        }
        
        result = optimize_supply_chain(factories, warehouses, customer_demand, transportation_costs)
        self.assertEqual(result["selected_factories"], expected["selected_factories"])
        self.assertEqual(result["selected_warehouses"], expected["selected_warehouses"])
        self.assertEqual(result["flow"], expected["flow"])
        self.assertAlmostEqual(result["total_cost"], expected["total_cost"], places=5)

    def test_infeasible(self):
        # Scenario: One factory cannot meet customer demand.
        factories = [{
            "location_id": "F1",
            "production_capacity": 30,
            "production_cost_per_unit": 1.0,
            "fixed_cost": 50.0
        }]
        
        warehouses = []
        
        customer_demand = [{
            "location_id": "C1",
            "demand": 50
        }]
        
        transportation_costs = {
            "F1": {"C1": 2.0},
            "C1": {}
        }
        
        expected = {
            "selected_factories": [],
            "selected_warehouses": [],
            "flow": {},
            "total_cost": float('inf')
        }
        
        result = optimize_supply_chain(factories, warehouses, customer_demand, transportation_costs)
        self.assertEqual(result["selected_factories"], expected["selected_factories"])
        self.assertEqual(result["selected_warehouses"], expected["selected_warehouses"])
        self.assertEqual(result["flow"], expected["flow"])
        self.assertTrue(math.isinf(result["total_cost"]))

    def test_large_scenario(self):
        # Scenario: Multiple factories, warehouses, and customers.
        factories = [
            {
                "location_id": "F1",
                "production_capacity": 100,
                "production_cost_per_unit": 1.0,
                "fixed_cost": 50.0
            },
            {
                "location_id": "F2",
                "production_capacity": 80,
                "production_cost_per_unit": 1.2,
                "fixed_cost": 40.0
            }
        ]
        
        warehouses = [
            {
                "location_id": "W1",
                "storage_capacity": 120,
                "storage_cost_per_unit": 0.8,
                "fixed_cost": 20.0
            },
            {
                "location_id": "W2",
                "storage_capacity": 50,
                "storage_cost_per_unit": 1.0,
                "fixed_cost": 15.0
            }
        ]
        
        customer_demand = [
            {"location_id": "C1", "demand": 40},
            {"location_id": "C2", "demand": 50},
            {"location_id": "C3", "demand": 30}
        ]
        
        # Transportation costs are defined between all locations.
        transportation_costs = {
            "F1": {"W1": 0.5, "W2": 1.0, "C1": 2.0, "C2": 2.5, "C3": 3.0},
            "F2": {"W1": 0.6, "W2": 0.9, "C1": 2.2, "C2": 2.3, "C3": 2.8},
            "W1": {"C1": 0.7, "C2": 0.8, "C3": 0.9},
            "W2": {"C1": 1.0, "C2": 1.1, "C3": 1.2},
            "C1": {},
            "C2": {},
            "C3": {}
        }
        
        result = optimize_supply_chain(factories, warehouses, customer_demand, transportation_costs)
        
        # Verify that all customer demands are met.
        customer_received = {cust["location_id"]: 0 for cust in customer_demand}
        for (src, dst), units in result["flow"].items():
            if dst in customer_received:
                customer_received[dst] += units
            # For warehouses, ensure net throughput is zero.
            if dst in [w["location_id"] for w in warehouses]:
                # Sum inflow equals outflow for warehouse node.
                pass
        
        for customer in customer_demand:
            self.assertEqual(customer_received[customer["location_id"]], customer["demand"])
        
        # Verify that the production from each opened factory does not exceed capacity.
        production = {}
        for (src, dst), units in result["flow"].items():
            if src in [f["location_id"] for f in factories]:
                production[src] = production.get(src, 0) + units
        for f in factories:
            if f["location_id"] in result["selected_factories"]:
                self.assertLessEqual(production.get(f["location_id"], 0), f["production_capacity"])
        
        # Verify warehouse net flow: inflow equals outflow for each selected warehouse.
        warehouse_inflow = {w["location_id"]: 0 for w in warehouses}
        warehouse_outflow = {w["location_id"]: 0 for w in warehouses}
        for (src, dst), units in result["flow"].items():
            if dst in warehouse_inflow:
                warehouse_inflow[dst] += units
            if src in warehouse_outflow:
                warehouse_outflow[src] += units
        for w in result["selected_warehouses"]:
            self.assertEqual(warehouse_inflow[w], warehouse_outflow[w])
        
        # Check that total cost is a finite positive number.
        self.assertIsInstance(result["total_cost"], float)
        self.assertGreater(result["total_cost"], 0.0)

if __name__ == '__main__':
    unittest.main()