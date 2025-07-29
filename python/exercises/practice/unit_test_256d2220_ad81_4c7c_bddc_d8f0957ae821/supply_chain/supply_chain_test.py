import unittest

from supply_chain import optimize_supply_chain

class SupplyChainTest(unittest.TestCase):
    def compute_total_cost(self, plan, transportation_costs, fixed_warehouse_costs):
        """Helper function to compute the total cost from the shipping plan."""
        used_warehouses = set()
        transport_cost = 0
        for (warehouse_id, zone_id), quantity in plan.items():
            transport_cost += quantity * transportation_costs[(warehouse_id, zone_id)]
            if quantity > 0:
                used_warehouses.add(warehouse_id)
        fixed_cost = sum(fixed_warehouse_costs[w] for w in used_warehouses)
        return transport_cost + fixed_cost

    def verify_plan(self, plan, warehouses, customer_zones):
        """Verify that the plan satisfies demand and capacity constraints."""
        # Build dictionaries for quick lookup
        capacity = {w_id: cap for w_id, cap in warehouses}
        demand = {z_id: dem for z_id, dem in customer_zones}
        
        # Sum shipments by warehouse and by zone
        shipped_from = {w_id: 0 for w_id, _ in warehouses}
        shipped_to = {z_id: 0 for z_id, _ in customer_zones}
        
        for (w_id, z_id), amount in plan.items():
            shipped_from[w_id] += amount
            shipped_to[z_id] += amount

        for w_id, ship in shipped_from.items():
            self.assertLessEqual(ship, capacity[w_id], f"Warehouse {w_id} exceeds capacity")
        for z_id, ship in shipped_to.items():
            self.assertEqual(ship, demand[z_id], f"Demand for zone {z_id} not met")

    def test_basic_optimal_solution(self):
        warehouses = [(1, 100), (2, 150)]
        customer_zones = [(101, 80), (102, 120)]
        transportation_costs = {
            (1, 101): 2,
            (1, 102): 5,
            (2, 101): 3,
            (2, 102): 1
        }
        fixed_warehouse_costs = {1: 50, 2: 75}
        expected_total_cost = 405

        plan = optimize_supply_chain(warehouses, customer_zones, transportation_costs, fixed_warehouse_costs)
        # Verify that plan meets demand and capacity constraints.
        self.verify_plan(plan, warehouses, customer_zones)
        cost = self.compute_total_cost(plan, transportation_costs, fixed_warehouse_costs)
        self.assertEqual(cost, expected_total_cost, "Total cost does not match expected optimal cost.")

    def test_infeasible_capacity(self):
        warehouses = [(1, 50)]
        customer_zones = [(101, 60)]
        transportation_costs = {
            (1, 101): 5
        }
        fixed_warehouse_costs = {1: 20}
        with self.assertRaises(ValueError) as context:
            optimize_supply_chain(warehouses, customer_zones, transportation_costs, fixed_warehouse_costs)
        self.assertIn("capacity", str(context.exception).lower())

    def test_sparse_transportation_routes(self):
        # In this case, there is no route for one of the zones.
        warehouses = [(1, 100)]
        customer_zones = [(101, 50), (102, 50)]
        transportation_costs = {
            (1, 101): 4
            # Missing route from warehouse 1 to zone 102.
        }
        fixed_warehouse_costs = {1: 30}
        with self.assertRaises(ValueError) as context:
            optimize_supply_chain(warehouses, customer_zones, transportation_costs, fixed_warehouse_costs)
        self.assertIn("feasible", str(context.exception).lower())

    def test_multiple_warehouses_optimal_plan(self):
        warehouses = [(1, 100), (2, 80)]
        customer_zones = [(101, 60), (102, 70), (103, 50)]
        transportation_costs = {
            (1, 101): 3,
            (1, 102): 1,
            (1, 103): 4,
            (2, 101): 2,
            (2, 102): 4,
            (2, 103): 1
        }
        fixed_warehouse_costs = {1: 40, 2: 30}
        # Total demand is exactly 60+70+50 = 180; capacity sums to 100+80=180.
        # One optimal distribution:
        # - Use warehouse 2 for zone 101 (60 units) and part of zone 103 (20 units),
        # - Use warehouse 1 for zone 102 (70 units) and remainder of zone 103 (30 units)
        # Cost: warehouse 2: (60*2 + 20*1) = 120 + 20 = 140 plus fixed cost 30 = 170;
        #       warehouse 1: (70*1 + 30*4) = 70 + 120 = 190 plus fixed cost 40 = 230;
        # Total cost expected = 170 + 230 = 400.
        expected_total_cost = 400

        plan = optimize_supply_chain(warehouses, customer_zones, transportation_costs, fixed_warehouse_costs)
        self.verify_plan(plan, warehouses, customer_zones)
        cost = self.compute_total_cost(plan, transportation_costs, fixed_warehouse_costs)
        self.assertEqual(cost, expected_total_cost, "Total cost does not match expected value.")

if __name__ == "__main__":
    unittest.main()