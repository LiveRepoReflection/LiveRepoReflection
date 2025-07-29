import unittest
from intergalactic_routing import IntergalacticRouter

class TestIntergalacticRouter(unittest.TestCase):
    
    def setUp(self):
        # Basic test case from the problem description
        planets = [1, 2, 3, 4, 5, 6]
        subnets = [101, 102]
        planet_to_subnets = {
            1: [101],
            2: [101, 102],
            3: [101],
            4: [102],
            5: [102],
            6: [102]
        }
        subnet_graphs = {
            101: {
                1: [(2, 1.0), (3, 2.0)],
                2: [(1, 1.0), (3, 1.5)],
                3: [(1, 2.0), (2, 1.5)]
            },
            102: {
                2: [(4, 2.5), (5, 3.0)],
                4: [(2, 2.5), (5, 1.0), (6, 4.0)],
                5: [(2, 3.0), (4, 1.0), (6, 2.0)],
                6: [(4, 4.0), (5, 2.0)]
            }
        }
        transfer_cost = 5.0
        
        self.router = IntergalacticRouter(planets, subnets, planet_to_subnets, subnet_graphs, transfer_cost)
    
    def test_basic_routing(self):
        # Test the basic routing example from the problem
        path, cost = self.router.find_optimal_path(1, 6)
        self.assertEqual(path, [1, 2, 5, 6])
        self.assertAlmostEqual(cost, 11.0)
    
    def test_same_planet(self):
        # Test routing to the same planet
        path, cost = self.router.find_optimal_path(3, 3)
        self.assertEqual(path, [3])
        self.assertEqual(cost, 0)
    
    def test_direct_connection(self):
        # Test routing between directly connected planets
        path, cost = self.router.find_optimal_path(1, 2)
        self.assertEqual(path, [1, 2])
        self.assertAlmostEqual(cost, 1.0)
    
    def test_within_same_subnet(self):
        # Test routing within the same subnet
        path, cost = self.router.find_optimal_path(1, 3)
        self.assertEqual(path, [1, 3])
        self.assertAlmostEqual(cost, 2.0)
        
        path, cost = self.router.find_optimal_path(4, 6)
        self.assertEqual(path, [4, 5, 6])
        self.assertAlmostEqual(cost, 3.0)
    
    def test_cross_subnet_routing(self):
        # Test routing that requires crossing subnets
        path, cost = self.router.find_optimal_path(3, 4)
        self.assertEqual(path, [3, 2, 4])
        self.assertAlmostEqual(cost, 1.5 + 5.0 + 2.5)
    
    def test_no_path_exists(self):
        # Create a separate router with disconnected planets
        planets = [1, 2, 3, 4, 5]
        subnets = [101, 102]
        planet_to_subnets = {
            1: [101],
            2: [101],
            3: [102],
            4: [102],
            5: [] # Isolated planet
        }
        subnet_graphs = {
            101: {
                1: [(2, 1.0)],
                2: [(1, 1.0)]
            },
            102: {
                3: [(4, 1.0)],
                4: [(3, 1.0)]
            }
        }
        router = IntergalacticRouter(planets, subnets, planet_to_subnets, subnet_graphs, 5.0)
        
        # No path should exist from subnet 101 to 102 or to the isolated planet
        path, cost = router.find_optimal_path(1, 3)
        self.assertEqual(path, None)
        self.assertEqual(cost, float('inf'))
        
        path, cost = router.find_optimal_path(1, 5)
        self.assertEqual(path, None)
        self.assertEqual(cost, float('inf'))
    
    def test_edge_update(self):
        # Test updating edge costs
        # Before update, path should be 1 -> 2 -> 5 -> 6 with cost 11.0
        path_before, cost_before = self.router.find_optimal_path(1, 6)
        self.assertEqual(path_before, [1, 2, 5, 6])
        self.assertAlmostEqual(cost_before, 11.0)
        
        # Update the edge costs to make a different path cheaper
        edge_updates = [
            (102, 2, 4, 0.5),  # Make 2 -> 4 very cheap
            (102, 4, 6, 0.5)   # Make 4 -> 6 very cheap
        ]
        self.router.update_edge_costs(edge_updates)
        
        # After update, path should be 1 -> 2 -> 4 -> 6 with cost 7.0
        path_after, cost_after = self.router.find_optimal_path(1, 6)
        self.assertEqual(path_after, [1, 2, 4, 6])
        self.assertAlmostEqual(cost_after, 1.0 + 5.0 + 0.5 + 0.5)
    
    def test_large_network(self):
        # Create a larger network to test scalability
        import random
        random.seed(42)  # For reproducibility
        
        num_planets = 100
        num_subnets = 10
        planets = list(range(1, num_planets + 1))
        subnets = list(range(101, 101 + num_subnets))
        
        # Assign planets to subnets (each planet in 1-3 subnets)
        planet_to_subnets = {}
        for p in planets:
            num_assigned = random.randint(1, 3)
            planet_to_subnets[p] = random.sample(subnets, num_assigned)
        
        # Create subnet graphs
        subnet_graphs = {}
        for s in subnets:
            subnet_graphs[s] = {}
            planets_in_subnet = [p for p, subs in planet_to_subnets.items() if s in subs]
            
            if len(planets_in_subnet) <= 1:
                continue  # Skip subnets with 0 or 1 planets
                
            # Create a connected graph for each subnet
            for i, p1 in enumerate(planets_in_subnet):
                subnet_graphs[s][p1] = []
                # Connect to some other planets in the subnet
                for j, p2 in enumerate(planets_in_subnet):
                    if i != j and random.random() < 0.3:  # 30% chance of connection
                        cost = random.uniform(0.5, 5.0)
                        subnet_graphs[s][p1].append((p2, cost))
        
        large_router = IntergalacticRouter(planets, subnets, planet_to_subnets, subnet_graphs, 10.0)
        
        # Test routing between a few planet pairs
        for _ in range(5):
            source = random.choice(planets)
            dest = random.choice(planets)
            if source == dest:
                continue
            
            path, cost = large_router.find_optimal_path(source, dest)
            # We can't assert specific paths or costs, but we can check that the function runs
            # and returns something reasonable
            if path is not None:
                self.assertIsInstance(path, list)
                self.assertGreaterEqual(len(path), 2)
                self.assertEqual(path[0], source)
                self.assertEqual(path[-1], dest)
                self.assertGreater(cost, 0)
            else:
                self.assertEqual(cost, float('inf'))
    
    def test_multiple_updates(self):
        # Test multiple sequential updates
        edge_updates1 = [(101, 1, 2, 10.0)]  # Make the direct path expensive
        self.router.update_edge_costs(edge_updates1)
        
        # Now the path from 1 to 2 should be 1 -> 3 -> 2
        path1, cost1 = self.router.find_optimal_path(1, 2)
        self.assertEqual(path1, [1, 3, 2])
        self.assertAlmostEqual(cost1, 2.0 + 1.5)
        
        edge_updates2 = [(101, 1, 3, 20.0)]  # Make that path expensive too
        self.router.update_edge_costs(edge_updates2)
        
        # Now the direct path should be cheaper again
        path2, cost2 = self.router.find_optimal_path(1, 2)
        self.assertEqual(path2, [1, 2])
        self.assertAlmostEqual(cost2, 10.0)
        
        # Reset the costs back to original
        edge_updates3 = [
            (101, 1, 2, 1.0),
            (101, 1, 3, 2.0)
        ]
        self.router.update_edge_costs(edge_updates3)
        
        # Should be back to the original optimal path
        path3, cost3 = self.router.find_optimal_path(1, 2)
        self.assertEqual(path3, [1, 2])
        self.assertAlmostEqual(cost3, 1.0)
    
    def test_invalid_inputs(self):
        # Test with invalid planet IDs
        path, cost = self.router.find_optimal_path(999, 6)
        self.assertEqual(path, None)
        self.assertEqual(cost, float('inf'))
        
        path, cost = self.router.find_optimal_path(1, 999)
        self.assertEqual(path, None)
        self.assertEqual(cost, float('inf'))
        
        # Test with invalid edge updates
        with self.assertRaises(Exception):
            self.router.update_edge_costs([(999, 1, 2, 1.0)])
        
        with self.assertRaises(Exception):
            self.router.update_edge_costs([(101, 999, 2, 1.0)])


if __name__ == "__main__":
    unittest.main()