import unittest
from order_optimizer import optimize_order_placement

class OrderOptimizerTest(unittest.TestCase):
    def test_basic_functionality(self):
        warehouses = [
            {
                "id": 1,
                "capacity": {"A": 5, "B": 10},
                "shipping_cost": {"A": 1.0, "B": 2.0},
            },
            {
                "id": 2,
                "capacity": {"A": 10, "C": 5},
                "shipping_cost": {"A": 1.5, "C": 2.5},
            },
        ]
        orders = [
            {
                "id": 1,
                "products": {"A": 7, "B": 3},
            },
            {
                "id": 2,
                "products": {"A": 2, "C": 4},
            },
        ]
        result = optimize_order_placement(warehouses, orders)
        # Verify each product quantity for each order is fulfilled exactly as requested.
        for order in orders:
            order_id = order["id"]
            for product, required_quantity in order["products"].items():
                allocated_quantity = sum(result[order_id].get(product, {}).values())
                self.assertEqual(allocated_quantity, required_quantity)

    def test_product_not_in_any_warehouse(self):
        warehouses = [
            {
                "id": 1,
                "capacity": {"A": 10},
                "shipping_cost": {"A": 1.0},
            },
        ]
        orders = [
            {
                "id": 1,
                "products": {"B": 5},  # Product B is not available in any warehouse.
            },
        ]
        with self.assertRaises(Exception):
            optimize_order_placement(warehouses, orders)

    def test_warehouse_capacity_exceeded(self):
        warehouses = [
            {
                "id": 1,
                "capacity": {"A": 3},
                "shipping_cost": {"A": 1.0},
            },
            {
                "id": 2,
                "capacity": {"A": 2},
                "shipping_cost": {"A": 2.0},
            },
        ]
        orders = [
            {
                "id": 1,
                "products": {"A": 10},  # Required exceeds total capacity (3+2).
            },
        ]
        with self.assertRaises(Exception):
            optimize_order_placement(warehouses, orders)

    def test_multiple_optimal_solutions(self):
        warehouses = [
            {
                "id": 1,
                "capacity": {"A": 10},
                "shipping_cost": {"A": 1.0},
            },
            {
                "id": 2,
                "capacity": {"A": 10},
                "shipping_cost": {"A": 1.0},
            },
        ]
        orders = [
            {
                "id": 1,
                "products": {"A": 10},
            },
        ]
        result = optimize_order_placement(warehouses, orders)
        total_allocated = sum(result[1].get("A", {}).values())
        self.assertEqual(total_allocated, 10)
        for warehouse in warehouses:
            allocated = result[1].get("A", {}).get(warehouse["id"], 0)
            self.assertLessEqual(allocated, warehouse["capacity"]["A"])

    def test_real_world_complexity(self):
        # Create a larger scenario with multiple warehouses and orders.
        warehouses = []
        orders = []
        # Generate 50 warehouses with capacities and varied shipping costs.
        for i in range(1, 51):
            warehouses.append({
                "id": i,
                "capacity": {"A": 50, "B": 50},
                "shipping_cost": {"A": 1.0 + (i % 5) * 0.1, "B": 2.0 + (i % 3) * 0.2},
            })
        # Generate 20 orders requiring products A and B.
        for i in range(1, 21):
            orders.append({
                "id": i,
                "products": {"A": 30, "B": 20},
            })
        result = optimize_order_placement(warehouses, orders)
        for order in orders:
            order_id = order["id"]
            for product, required_quantity in order["products"].items():
                allocated_quantity = sum(result[order_id].get(product, {}).values())
                self.assertEqual(allocated_quantity, required_quantity)

if __name__ == "__main__":
    unittest.main()