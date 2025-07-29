import unittest
import math
from supply_chain_optimizer import Warehouse, Store, optimize_supply_chain

class TestSupplyChainOptimizer(unittest.TestCase):
    def setUp(self):
        # Create test warehouses
        self.warehouse1 = Warehouse(
            id="WH1",
            location=(40.7128, -74.0060),  # New York
            inventory={"P1": 100, "P2": 50}
        )
        self.warehouse2 = Warehouse(
            id="WH2",
            location=(34.0522, -118.2437),  # Los Angeles
            inventory={"P1": 200, "P2": 100}
        )
        
        # Create test stores
        self.store1 = Store(
            id="ST1",
            location=(41.8781, -87.6298),  # Chicago
            demand={"P1": 80, "P2": 30},
            unfulfilled_penalty={"P1": 5.0, "P2": 3.0}
        )
        self.store2 = Store(
            id="ST2",
            location=(29.7604, -95.3698),  # Houston
            demand={"P1": 50, "P2": 20},
            unfulfilled_penalty={"P1": 4.0, "P2": 2.5}
        )
        
        self.transportation_rate = 0.1  # Cost per km per unit

    def test_basic_optimization(self):
        """Test basic optimization scenario"""
        warehouses = [self.warehouse1, self.warehouse2]
        stores = [self.store1, self.store2]
        
        result = optimize_supply_chain(warehouses, stores, self.transportation_rate)
        
        # Verify all shipments are non-negative integers
        for key, quantity in result.items():
            self.assertIsInstance(quantity, int)
            self.assertGreaterEqual(quantity, 0)
            
        # Verify warehouse capacities aren't exceeded
        for wh in warehouses:
            for product in wh.inventory:
                total_shipped = sum(
                    qty for (wh_id, _, prod_id), qty in result.items()
                    if wh_id == wh.id and prod_id == product
                )
                self.assertLessEqual(total_shipped, wh.inventory[product])

    def test_unfulfilled_demand_penalty(self):
        """Test that system properly accounts for unfulfilled demand penalties"""
        # Create a warehouse with limited inventory
        limited_warehouse = Warehouse(
            id="WH3",
            location=(39.9526, -75.1652),  # Philadelphia
            inventory={"P1": 10}  # Very limited inventory
        )
        
        high_demand_store = Store(
            id="ST3",
            location=(38.9072, -77.0369),  # Washington DC
            demand={"P1": 100},
            unfulfilled_penalty={"P1": 100.0}  # Very high penalty
        )
        
        result = optimize_supply_chain(
            [limited_warehouse],
            [high_demand_store],
            self.transportation_rate
        )
        
        # Should ship all available inventory despite distance
        total_shipped = sum(
            qty for (_, _, prod_id), qty in result.items()
            if prod_id == "P1"
        )
        self.assertEqual(total_shipped, limited_warehouse.inventory["P1"])

    def test_no_inventory_case(self):
        """Test scenario where no inventory is available"""
        empty_warehouse = Warehouse(
            id="WH4",
            location=(32.7157, -117.1611),  # San Diego
            inventory={}  # No inventory
        )
        
        result = optimize_supply_chain(
            [empty_warehouse],
            [self.store1],
            self.transportation_rate
        )
        
        # Should return empty shipping plan
        self.assertEqual(len(result), 0)

    def test_distance_calculation(self):
        """Verify distance affects shipping decisions"""
        # Two warehouses at different distances from store
        close_warehouse = Warehouse(
            id="WH5",
            location=(37.7749, -122.4194),  # San Francisco
            inventory={"P1": 100}
        )
        far_warehouse = Warehouse(
            id="WH6",
            location=(47.6062, -122.3321),  # Seattle
            inventory={"P1": 100}
        )
        
        store = Store(
            id="ST4",
            location=(37.3382, -121.8863),  # San Jose
            demand={"P1": 50},
            unfulfilled_penalty={"P1": 1.0}  # Low penalty
        )
        
        result = optimize_supply_chain(
            [close_warehouse, far_warehouse],
            [store],
            self.transportation_rate
        )
        
        # Should prefer shipping from closer warehouse
        close_shipped = sum(
            qty for (wh_id, _, prod_id), qty in result.items()
            if wh_id == close_warehouse.id and prod_id == "P1"
        )
        self.assertGreater(close_shipped, 0)

    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        with self.assertRaises(ValueError):
            optimize_supply_chain([], [self.store1], self.transportation_rate)
            
        with self.assertRaises(ValueError):
            optimize_supply_chain([self.warehouse1], [], self.transportation_rate)
            
        with self.assertRaises(ValueError):
            optimize_supply_chain([self.warehouse1], [self.store1], -0.1)

if __name__ == '__main__':
    unittest.main()