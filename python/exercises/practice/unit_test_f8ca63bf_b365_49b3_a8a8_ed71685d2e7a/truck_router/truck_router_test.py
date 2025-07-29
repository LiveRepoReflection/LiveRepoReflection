import unittest
from truck_router import minimal_trucks

class TruckRouterTest(unittest.TestCase):
    def test_empty_orders(self):
        warehouses = {"A": 100}
        orders = []
        truck_capacity = 50
        expected = 0
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_combinable_orders(self):
        # Two orders from A to B that sum exactly to truck capacity.
        warehouses = {"A": 200, "B": 200}
        orders = [("A", "B", 30), ("A", "B", 20)]
        truck_capacity = 50
        expected = 1  # Both orders can be combined into one truck.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_separated_orders(self):
        # Two orders from A to B that require two trucks when combined optimally.
        warehouses = {"A": 200, "B": 200}
        orders = [("A", "B", 30), ("A", "B", 40)]
        truck_capacity = 50
        expected = 2  # Cannot fit 70 units in one truck.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_invalid_warehouse_ids(self):
        # Orders with non-existent warehouses should be ignored.
        warehouses = {"A": 200, "B": 200}
        orders = [("A", "B", 20), ("X", "B", 30), ("A", "Y", 10)]
        truck_capacity = 30
        expected = 1  # Only valid order is ("A", "B", 20) which fits in one truck.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_zero_quantity(self):
        # Zero quantity orders should not affect the truck count.
        warehouses = {"A": 100, "B": 100}
        orders = [("A", "B", 0), ("A", "B", 40)]
        truck_capacity = 40
        expected = 1  # Only the 40 unit order counts.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_splitting_order(self):
        # A single order that must be split across trucks.
        warehouses = {"A": 150, "B": 150}
        orders = [("A", "B", 120)]
        truck_capacity = 70
        expected = 2  # 120 units require two trucks (one with 70 and one with 50).
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_impossible_due_to_capacity(self):
        # When the destination warehouse's capacity is exceeded, fulfilling orders is impossible.
        warehouses = {"A": 150, "B": 50}
        orders = [("A", "B", 40), ("A", "B", 20)]
        truck_capacity = 50
        expected = -1  # B cannot receive more than 50 units.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_complex_optimal(self):
        # A more complex scenario with orders from different pairs.
        warehouses = {"A": 200, "B": 200, "C": 200}
        orders = [("A", "B", 40), ("A", "C", 30), ("B", "C", 20), ("A", "B", 10)]
        truck_capacity = 50
        expected = 2  # Orders can be optimally arranged into two trucks.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

    def test_all_invalid_orders(self):
        # When all orders refer to invalid warehouse IDs, they are ignored.
        warehouses = {"A": 200, "B": 200}
        orders = [("X", "Y", 50)]
        truck_capacity = 50
        expected = 0  # No valid orders, so no trucks are needed.
        self.assertEqual(minimal_trucks(warehouses, orders, truck_capacity), expected)

if __name__ == '__main__':
    unittest.main()