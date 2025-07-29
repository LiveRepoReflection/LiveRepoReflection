import unittest
from network_augment import optimize_network

class TestNetworkAugment(unittest.TestCase):
    
    def test_basic_network(self):
        """Test with a small network with obvious optimal solution."""
        # Create a simple network with 4 nodes
        existing_network = {
            0: {1: (5, 100), 2: (7, 100)},
            1: {3: (4, 100)},
            2: {3: (6, 100)},
            3: {}
        }
        
        commute_data = [
            (0, 3, 1000),  # 1000 people commuting from 0 to 3
        ]
        
        potential_hubs = [
            (4, 50),  # Location 4 with cost 50
            (5, 80),  # Location 5 with cost 80
        ]
        
        # Define geographical distances for calculating travel times
        hub_distances = {
            4: {0: 2, 1: 2, 2: 2, 3: 2},
            5: {0: 1, 1: 1, 2: 1, 3: 1}
        }
        
        budget = 100
        hub_capacity = 2000
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=100
        )
        
        # The optimal solution should include hub 5 (faster connections)
        self.assertEqual(result, [5])
        
    def test_budget_constraint(self):
        """Test that the function respects the budget constraint."""
        existing_network = {
            0: {1: (5, 100)},
            1: {}
        }
        
        commute_data = [
            (0, 1, 100),
        ]
        
        potential_hubs = [
            (2, 100),  # Location 2 with cost 100
            (3, 101),  # Location 3 with cost 101 (exceeds budget)
        ]
        
        hub_distances = {
            2: {0: 1, 1: 1},
            3: {0: 0.5, 1: 0.5}  # Better but too expensive
        }
        
        budget = 100
        hub_capacity = 200
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=100
        )
        
        # Should only include hub 2, as hub 3 exceeds budget
        self.assertEqual(result, [2])
        
    def test_capacity_constraint(self):
        """Test that the function respects the hub capacity constraint."""
        existing_network = {
            0: {2: (10, 100)},
            1: {2: (10, 100)},
            2: {}
        }
        
        commute_data = [
            (0, 2, 600),
            (1, 2, 600),
        ]
        
        potential_hubs = [
            (3, 50),  # Location 3 with cost 50
            (4, 50),  # Location 4 with cost 50
        ]
        
        hub_distances = {
            3: {0: 2, 1: 8, 2: 3},
            4: {0: 8, 1: 2, 2: 3}
        }
        
        budget = 100
        hub_capacity = 700  # Each hub can handle at most 700 people
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=1000
        )
        
        # Should include both hubs to distribute the load
        self.assertCountEqual(result, [3, 4])
        
    def test_multiple_optimal_solutions(self):
        """Test when multiple optimal solutions exist."""
        existing_network = {
            0: {2: (10, 100)},
            1: {3: (10, 100)},
            2: {},
            3: {}
        }
        
        commute_data = [
            (0, 2, 100),
            (1, 3, 100),
        ]
        
        potential_hubs = [
            (4, 40),  # Location 4 with cost 40
            (5, 40),  # Location 5 with cost 40 (identical to 4)
        ]
        
        hub_distances = {
            4: {0: 2, 1: 2, 2: 2, 3: 2},
            5: {0: 2, 1: 2, 2: 2, 3: 2}  # Identical distances
        }
        
        budget = 40
        hub_capacity = 200
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=100
        )
        
        # Either 4 or 5 is valid
        self.assertTrue(result == [4] or result == [5])
        
    def test_no_solution_within_budget(self):
        """Test when no solution is possible within budget."""
        existing_network = {
            0: {1: (5, 100)},
            1: {}
        }
        
        commute_data = [
            (0, 1, 100),
        ]
        
        potential_hubs = [
            (2, 101),  # Location 2 with cost 101 (exceeds budget)
        ]
        
        hub_distances = {
            2: {0: 1, 1: 1},
        }
        
        budget = 100
        hub_capacity = 200
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=100
        )
        
        # Should return empty list as no hub can be built within budget
        self.assertEqual(result, [])
        
    def test_no_solution_within_capacity(self):
        """Test when no solution is possible due to capacity constraints."""
        existing_network = {
            0: {1: (5, 100)},
            1: {}
        }
        
        commute_data = [
            (0, 1, 1000),  # 1000 people, but hub capacity is only 500
        ]
        
        potential_hubs = [
            (2, 50),  # Location 2 with cost 50
        ]
        
        hub_distances = {
            2: {0: 1, 1: 1},
        }
        
        budget = 100
        hub_capacity = 500  # Not enough capacity for 1000 people
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=100
        )
        
        # Should return empty list as the capacity constraint cannot be met
        self.assertEqual(result, [])
        
    def test_complex_network(self):
        """Test with a more complex network."""
        # Create a more complex network
        existing_network = {
            0: {1: (3, 100), 2: (5, 100)},
            1: {3: (4, 100), 4: (2, 100)},
            2: {5: (6, 100)},
            3: {6: (2, 100)},
            4: {6: (5, 100)},
            5: {6: (4, 100)},
            6: {}
        }
        
        commute_data = [
            (0, 6, 500),  # 500 people from 0 to 6
            (1, 6, 300),  # 300 people from 1 to 6
            (2, 6, 400),  # 400 people from 2 to 6
        ]
        
        potential_hubs = [
            (7, 150),  # Location 7 with cost 150
            (8, 100),  # Location 8 with cost 100
            (9, 200),  # Location 9 with cost 200
        ]
        
        hub_distances = {
            7: {0: 2, 1: 3, 2: 3, 3: 2, 4: 2, 5: 3, 6: 1},
            8: {0: 4, 1: 3, 2: 2, 3: 4, 4: 3, 5: 2, 6: 2},
            9: {0: 1, 1: 2, 2: 3, 3: 2, 4: 3, 5: 4, 6: 1}
        }
        
        budget = 300
        hub_capacity = 800
        
        result = optimize_network(
            existing_network=existing_network,
            commute_data=commute_data,
            potential_hubs=potential_hubs,
            hub_distances=hub_distances,
            budget=budget,
            hub_capacity=hub_capacity,
            edge_capacity=1000
        )
        
        # Verify that result contains valid hub locations within budget
        total_cost = sum(cost for loc, cost in potential_hubs if loc in result)
        self.assertTrue(total_cost <= budget)
        
        # Should include at least one hub for optimality
        self.assertTrue(len(result) > 0)
        
        # Check all results are from potential hubs
        potential_hub_ids = [loc for loc, _ in potential_hubs]
        for hub in result:
            self.assertIn(hub, potential_hub_ids)

if __name__ == '__main__':
    unittest.main()