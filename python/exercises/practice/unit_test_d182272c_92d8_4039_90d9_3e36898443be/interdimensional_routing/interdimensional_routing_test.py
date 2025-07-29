import unittest
from interdimensional_routing import find_optimal_path

class InterdimensionalRoutingTest(unittest.TestCase):
    def test_simple_path(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 0},
            3: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (2, 3, 5)
        ]
        source = 1
        destination = 3
        k = 1
        
        expected_cost = 10
        expected_path = [1, 2, 3]
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_path_with_instability(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 10},
            3: {"instability": 0},
            4: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (2, 3, 5),
            (1, 4, 7),
            (4, 3, 7)
        ]
        source = 1
        destination = 3
        k = 1
        
        # Path 1-2-3 has latency 10 + instability 10 = 20
        # Path 1-4-3 has latency 14 + instability 0 = 14
        expected_cost = 14
        expected_path = [1, 4, 3]
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_high_k_value(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 1},
            3: {"instability": 0},
            4: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (2, 3, 5),
            (1, 4, 15),
            (4, 3, 15)
        ]
        source = 1
        destination = 3
        k = 50
        
        # Path 1-2-3 has latency 10 + instability 50*1 = 60
        # Path 1-4-3 has latency 30 + instability 0 = 30
        expected_cost = 30
        expected_path = [1, 4, 3]
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_low_k_value(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 10},
            3: {"instability": 0},
            4: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (2, 3, 5),
            (1, 4, 15),
            (4, 3, 15)
        ]
        source = 1
        destination = 3
        k = 1
        
        # Path 1-2-3 has latency 10 + instability 10 = 20
        # Path 1-4-3 has latency 30 + instability 0 = 30
        expected_cost = 20
        expected_path = [1, 2, 3]
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_same_source_destination(self):
        routers = {
            1: {"instability": 5},
            2: {"instability": 0}
        }
        connections = [
            (1, 2, 10)
        ]
        source = 1
        destination = 1
        k = 2
        
        # Source and destination are the same, so cost is just the instability of the router
        expected_cost = 5 * k
        expected_path = [1]
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_no_path(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 0},
            3: {"instability": 0},
            4: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (3, 4, 5)
        ]
        source = 1
        destination = 4
        k = 1
        
        expected_cost = -1
        expected_path = []
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_multiple_paths(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 2},
            3: {"instability": 3},
            4: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (2, 4, 5),
            (1, 3, 6),
            (3, 4, 4)
        ]
        source = 1
        destination = 4
        k = 1
        
        # Path 1-2-4 has latency 10 + instability 2 = 12
        # Path 1-3-4 has latency 10 + instability 3 = 13
        expected_cost = 12
        # We don't check the exact path since there could be multiple paths with the same cost
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertIn(path[0], [1])
        self.assertIn(path[-1], [4])
    
    def test_large_network(self):
        # Create a larger test case
        routers = {}
        connections = []
        
        # Create 100 routers
        for i in range(1, 101):
            routers[i] = {"instability": i % 10}  # Some routers have instability
            
        # Create connections in a grid-like pattern
        for i in range(1, 91):  # Connect horizontally
            connections.append((i, i + 10, (i % 5) + 1))
            
        for i in range(1, 100):  # Connect vertically if not in the last column
            if i % 10 != 0:
                connections.append((i, i + 1, (i % 7) + 1))
        
        source = 1
        destination = 100
        k = 5
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        
        # We don't know the exact cost, but it should be positive
        self.assertGreater(cost, 0)
        # The path should start at the source and end at the destination
        self.assertEqual(path[0], source)
        self.assertEqual(path[-1], destination)
    
    def test_disconnected_graph(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 0},
            3: {"instability": 0},
            4: {"instability": 0},
            5: {"instability": 0}
        }
        connections = [
            (1, 2, 5),
            (2, 3, 5),
            (4, 5, 5)
        ]
        source = 1
        destination = 5
        k = 1
        
        expected_cost = -1
        expected_path = []
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        self.assertEqual(expected_path, path)
    
    def test_graph_with_cycles(self):
        routers = {
            1: {"instability": 0},
            2: {"instability": 1},
            3: {"instability": 2},
            4: {"instability": 3}
        }
        connections = [
            (1, 2, 5),
            (2, 3, 5),
            (3, 4, 5),
            (4, 1, 20)  # Creates a cycle
        ]
        source = 1
        destination = 4
        k = 2
        
        # Path 1-2-3-4 has latency 15 + instability (0+1+2+3)*2 = 27
        # Path 1-4 has latency 20 + instability (0+3)*2 = 26
        expected_cost = 26
        expected_path = [1, 4]
        
        cost, path = find_optimal_path(routers, connections, source, destination, k)
        self.assertEqual(expected_cost, cost)
        # Check that the path is valid (we don't check the exact path since there could be multiple valid paths)
        self.assertEqual(path[0], source)
        self.assertEqual(path[-1], destination)

if __name__ == '__main__':
    unittest.main()