import unittest
from optimal_warehousing import assign_orders

class TestOptimalWarehousing(unittest.TestCase):
    def setUp(self):
        # Common helper to compute total volume for an order
        self.get_order_volume = lambda order: sum(order["volumes"])
        
    def validate_assignment(self, warehouses, orders, product_dependencies, assignment):
        # Create lookup for orders by order_id
        order_lookup = {order["order_id"]: order for order in orders}
        
        # Check that each order is assigned at most once
        assigned_orders = set()
        for wh_id, order_ids in assignment.items():
            for oid in order_ids:
                self.assertNotIn(oid, assigned_orders, f"Order {oid} assigned multiple times.")
                assigned_orders.add(oid)
                
        # Check capacity constraints for each warehouse
        for wh_id, order_ids in assignment.items():
            total_volume = 0
            capacity = warehouses[wh_id]["capacity"]
            for oid in order_ids:
                order = order_lookup[oid]
                total_volume += self.get_order_volume(order)
            self.assertLessEqual(total_volume, capacity, f"Warehouse {wh_id} capacity exceeded.")
            
        # Check product dependency constraints
        # A dependency (product, required_wh) implies that if an order contains that product,
        # then if it is assigned, it must be assigned to that required_wh.
        for order in orders:
            oid = order["order_id"]
            assigned_wh = None
            for wh_id, order_ids in assignment.items():
                if oid in order_ids:
                    assigned_wh = wh_id
                    break
            for prod, req_wh in product_dependencies:
                if prod in order["products"]:
                    # if order is assigned, it must be to the dependent warehouse
                    if assigned_wh is not None:
                        self.assertEqual(assigned_wh, req_wh, 
                                         f"Order {oid} contains product {prod} but assigned to warehouse {assigned_wh} instead of required {req_wh}.")

    def test_single_order_no_dependency(self):
        warehouses = {
            1: {"capacity": 500, "cost": 200},
            2: {"capacity": 300, "cost": 150}
        }
        orders = [
            {"order_id": 1, "products": [10], "volumes": [100], "preferred_warehouses": [1, 2]}
        ]
        product_dependencies = []
        
        assignment = assign_orders(warehouses, orders, product_dependencies)
        # Validate that the order is assigned and constraints are met.
        self.validate_assignment(warehouses, orders, product_dependencies, assignment)
        # Check that order 1 is assigned to one of the provided warehouses
        assigned_wh = None
        for wh, oids in assignment.items():
            if 1 in oids:
                assigned_wh = wh
                break
        self.assertIsNotNone(assigned_wh, "Order 1 should be assigned to a warehouse.")
        self.assertIn(assigned_wh, [1, 2], "Order 1 assigned to an unexpected warehouse.")

    def test_order_with_dependency(self):
        warehouses = {
            1: {"capacity": 400, "cost": 250},
            2: {"capacity": 400, "cost": 300}
        }
        # Order 1 contains product 5 which has a dependency requiring warehouse 2.
        orders = [
            {"order_id": 1, "products": [5, 7], "volumes": [150, 100], "preferred_warehouses": [1, 2]},
            {"order_id": 2, "products": [8], "volumes": [200], "preferred_warehouses": [1, 2]}
        ]
        product_dependencies = [(5, 2)]
        
        assignment = assign_orders(warehouses, orders, product_dependencies)
        self.validate_assignment(warehouses, orders, product_dependencies, assignment)
        # Verify that order 1 is assigned to warehouse 2 due to dependency
        self.assertIn(2, assignment, "Warehouse 2 should be used due to product dependency.")
        self.assertIn(1, assignment[2], "Order 1 must be assigned to warehouse 2 because of product dependency.")
    
    def test_insufficient_capacity(self):
        warehouses = {
            1: {"capacity": 100, "cost": 200},
            2: {"capacity": 100, "cost": 150}
        }
        # Orders exceed warehouse capacities; order 2 should not be assigned.
        orders = [
            {"order_id": 1, "products": [1], "volumes": [90], "preferred_warehouses": [1, 2]},
            {"order_id": 2, "products": [2], "volumes": [50], "preferred_warehouses": [1, 2]},
            {"order_id": 3, "products": [3], "volumes": [60], "preferred_warehouses": [2, 1]}
        ]
        product_dependencies = []
        
        assignment = assign_orders(warehouses, orders, product_dependencies)
        self.validate_assignment(warehouses, orders, product_dependencies, assignment)
        # Check that orders that cannot fit are not assigned.
        assigned_ids = {oid for oids in assignment.values() for oid in oids}
        for order in orders:
            total_order_volume = self.get_order_volume(order)
            # If an order's volume exceeds any warehouse's remaining capacity, it might not be assigned.
            if total_order_volume > max(wh["capacity"] for wh in warehouses.values()):
                self.assertNotIn(order["order_id"], assigned_ids)
    
    def test_multiple_orders_mixed(self):
        warehouses = {
            1: {"capacity": 800, "cost": 400},
            2: {"capacity": 600, "cost": 350},
            3: {"capacity": 1000, "cost": 500}
        }
        orders = [
            {"order_id": 1, "products": [10, 11], "volumes": [200, 100], "preferred_warehouses": [1, 2, 3]},
            {"order_id": 2, "products": [12], "volumes": [300], "preferred_warehouses": [2, 1, 3]},
            {"order_id": 3, "products": [13, 14], "volumes": [150, 150], "preferred_warehouses": [3, 1, 2]},
            {"order_id": 4, "products": [15], "volumes": [400], "preferred_warehouses": [1, 3, 2]},
            {"order_id": 5, "products": [16], "volumes": [100], "preferred_warehouses": [2, 3, 1]}
        ]
        # Order 4 has a dependency to warehouse 1 and order 3 has dependency to warehouse 3.
        product_dependencies = [(15, 1), (13, 3)]
        
        assignment = assign_orders(warehouses, orders, product_dependencies)
        self.validate_assignment(warehouses, orders, product_dependencies, assignment)
        
        # Ensure that dependency orders are assigned correctly
        for wh_id, order_ids in assignment.items():
            for oid in order_ids:
                order = next(o for o in orders if o["order_id"] == oid)
                if 15 in order["products"]:
                    self.assertEqual(wh_id, 1, "Order with product 15 must be assigned to warehouse 1.")
                if 13 in order["products"]:
                    self.assertEqual(wh_id, 3, "Order with product 13 must be assigned to warehouse 3.")
    
    def test_no_assignable_orders(self):
        warehouses = {
            1: {"capacity": 100, "cost": 250},
            2: {"capacity": 100, "cost": 200}
        }
        # Orders have volumes that exceed all warehouse capacities.
        orders = [
            {"order_id": 1, "products": [1], "volumes": [150], "preferred_warehouses": [1]},
            {"order_id": 2, "products": [2], "volumes": [200], "preferred_warehouses": [2]}
        ]
        product_dependencies = []
        
        assignment = assign_orders(warehouses, orders, product_dependencies)
        # Validate that assignment does not violate constraints.
        self.validate_assignment(warehouses, orders, product_dependencies, assignment)
        # None of the orders should be assigned.
        all_assigned_orders = {oid for order_list in assignment.values() for oid in order_list}
        self.assertEqual(all_assigned_orders, set(), "No orders should be assigned when none fit capacity.")

if __name__ == "__main__":
    unittest.main()