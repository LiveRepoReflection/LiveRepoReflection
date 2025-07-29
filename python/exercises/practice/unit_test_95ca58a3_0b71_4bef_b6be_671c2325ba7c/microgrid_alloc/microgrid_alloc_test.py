import unittest
from microgrid_alloc import allocate

class MicrogridAllocTest(unittest.TestCase):
    def test_grid_only_scenario(self):
        # Scenario: Single grid resource, one consumer, one time step.
        resources = [
            {
                "type": "grid",
                "capacity": float('inf'),
                "cost": [0.25]
            }
        ]
        consumers = [
            [10]  # One consumer with a demand of 10 kWh for one time step.
        ]
        time_steps = 1
        output = allocate(resources, consumers, time_steps)
        
        # Verify output structure
        self.assertIsInstance(output, dict)
        self.assertIn("allocations", output)
        self.assertIn("total_cost", output)
        allocations = output["allocations"]
        self.assertEqual(len(allocations), time_steps)
        for t in range(time_steps):
            self.assertEqual(len(allocations[t]), len(resources))
            # The total allocation should meet the aggregated consumer demand.
            total_demand = sum(consumer[t] for consumer in consumers)
            self.assertAlmostEqual(sum(allocations[t]), total_demand, places=5)
        
        # Verify cost: For grid, cost per kWh multiplies allocation.
        expected_cost = sum(allocations[t][0] * resources[0]["cost"][t] for t in range(time_steps))
        self.assertAlmostEqual(output["total_cost"], expected_cost, places=5)

    def test_solar_and_battery_scenario(self):
        # Scenario: One solar resource and one battery resource with one consumer over 2 time steps.
        resources = [
            {
                "type": "solar",
                "capacity": 10,
                "availability": [0.5, 0.8]
            },
            {
                "type": "battery",
                "capacity": 5,
                "initial_charge": 2,
                "charge_rate": 2,
                "discharge_rate": 2,
                "degradation_cost": 0.1
            }
        ]
        consumers = [
            [3, 4]  # One consumer with demand 3 kWh at t=0 and 4 kWh at t=1.
        ]
        time_steps = 2
        output = allocate(resources, consumers, time_steps)
        
        # Verify output structure
        self.assertIsInstance(output, dict)
        self.assertIn("allocations", output)
        self.assertIn("total_cost", output)
        allocations = output["allocations"]
        self.assertEqual(len(allocations), time_steps)
        
        for t in range(time_steps):
            self.assertEqual(len(allocations[t]), len(resources))
            # Aggregated demand check
            total_demand = sum(consumer[t] for consumer in consumers)
            self.assertAlmostEqual(sum(allocations[t]), total_demand, places=5)
            # Verify solar allocation does not exceed (capacity * availability)
            solar_alloc = allocations[t][0]
            self.assertLessEqual(solar_alloc, resources[0]["capacity"] * resources[0]["availability"][t])
        
        # Check that the total cost is computed to be non-negative.
        self.assertGreaterEqual(output["total_cost"], 0)

    def test_multiple_consumers_and_resources(self):
        # Scenario: Multiple resources (solar, wind, battery, grid) and multiple consumers over 3 time steps.
        resources = [
            {
                "type": "solar",
                "capacity": 8,
                "availability": [0.6, 0.6, 0.7]
            },
            {
                "type": "wind",
                "capacity": 5,
                "availability": [0.5, 0.7, 0.6]
            },
            {
                "type": "battery",
                "capacity": 4,
                "initial_charge": 2,
                "charge_rate": 2,
                "discharge_rate": 2,
                "degradation_cost": 0.05
            },
            {
                "type": "grid",
                "capacity": float('inf'),
                "cost": [0.3, 0.25, 0.35]
            }
        ]
        consumers = [
            [4, 5, 3],  # Consumer 1 demands
            [2, 3, 4]   # Consumer 2 demands
        ]
        time_steps = 3
        output = allocate(resources, consumers, time_steps)
        
        # Verify output structure.
        self.assertIsInstance(output, dict)
        self.assertIn("allocations", output)
        self.assertIn("total_cost", output)
        allocations = output["allocations"]
        self.assertEqual(len(allocations), time_steps)
        
        # Compute total expected demand per time step
        total_demands = [sum(consumer[t] for consumer in consumers) for t in range(time_steps)]
        
        for t in range(time_steps):
            self.assertEqual(len(allocations[t]), len(resources))
            self.assertAlmostEqual(sum(allocations[t]), total_demands[t], places=5)
            # Check constraints for renewable resources.
            solar_alloc = allocations[t][0]
            wind_alloc = allocations[t][1]
            self.assertLessEqual(solar_alloc, resources[0]["capacity"] * resources[0]["availability"][t])
            self.assertLessEqual(wind_alloc, resources[1]["capacity"] * resources[1]["availability"][t])
        
        # Total cost should be non-negative.
        self.assertGreaterEqual(output["total_cost"], 0)

if __name__ == '__main__':
    unittest.main()