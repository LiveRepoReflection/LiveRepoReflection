import unittest
from optimal_router import find_optimal_route

class TestOptimalRouter(unittest.TestCase):
    def setUp(self):
        # Basic test graph
        self.basic_graph = {
            'A': {'B': 10, 'C': 15},
            'B': {'D': 12, 'E': 15},
            'C': {'F': 10},
            'D': {'F': 2, 'G': 1},
            'E': {'G': 9},
            'F': {'G': 5},
            'G': {}
        }

        # Larger test graph
        self.large_graph = {}
        # Create a 10x10 grid graph
        for i in range(10):
            for j in range(10):
                node = f'{i},{j}'
                self.large_graph[node] = {}
                if i > 0:
                    self.large_graph[node][f'{i-1},{j}'] = 1
                if i < 9:
                    self.large_graph[node][f'{i+1},{j}'] = 1
                if j > 0:
                    self.large_graph[node][f'{i},{j-1}'] = 1
                if j < 9:
                    self.large_graph[node][f'{i},{j+1}'] = 1

    def test_basic_route(self):
        request = {
            'source': 'A',
            'destination': 'G',
            'max_travel_time': 25,
            'priority': 1
        }
        route = find_optimal_route(self.basic_graph, request)
        self.assertIsNotNone(route)
        self.assertEqual(route[0], 'A')
        self.assertEqual(route[-1], 'G')
        
        # Calculate total time
        total_time = 0
        for i in range(len(route)-1):
            total_time += self.basic_graph[route[i]][route[i+1]]
        self.assertLessEqual(total_time, request['max_travel_time'])

    def test_no_valid_route(self):
        request = {
            'source': 'A',
            'destination': 'G',
            'max_travel_time': 10,  # Too short to reach G
            'priority': 1
        }
        route = find_optimal_route(self.basic_graph, request)
        self.assertEqual(route, [])

    def test_large_graph_performance(self):
        request = {
            'source': '0,0',
            'destination': '9,9',
            'max_travel_time': 100,
            'priority': 1
        }
        import time
        start_time = time.time()
        route = find_optimal_route(self.large_graph, request)
        end_time = time.time()
        
        self.assertLessEqual(end_time - start_time, 0.5)  # Should complete within 500ms
        self.assertIsNotNone(route)
        self.assertEqual(route[0], '0,0')
        self.assertEqual(route[-1], '9,9')

    def test_edge_updates(self):
        graph = dict(self.basic_graph)
        request = {
            'source': 'A',
            'destination': 'G',
            'max_travel_time': 25,
            'priority': 1
        }
        
        # Get initial route
        initial_route = find_optimal_route(graph, request)
        
        # Update edge weight
        graph['B']['D'] = 100  # Make this path very expensive
        
        # Get new route
        new_route = find_optimal_route(graph, request)
        
        self.assertNotEqual(initial_route, new_route)

    def test_same_source_destination(self):
        request = {
            'source': 'A',
            'destination': 'A',
            'max_travel_time': 10,
            'priority': 1
        }
        route = find_optimal_route(self.basic_graph, request)
        self.assertEqual(route, ['A'])

    def test_priority_handling(self):
        requests = [
            {
                'source': 'A',
                'destination': 'G',
                'max_travel_time': 25,
                'priority': 1
            },
            {
                'source': 'A',
                'destination': 'G',
                'max_travel_time': 30,
                'priority': 2
            }
        ]
        
        # Both routes should be valid but might be different due to priority
        route1 = find_optimal_route(self.basic_graph, requests[0])
        route2 = find_optimal_route(self.basic_graph, requests[1])
        
        self.assertIsNotNone(route1)
        self.assertIsNotNone(route2)

    def test_cycle_handling(self):
        # Graph with cycles
        cyclic_graph = {
            'A': {'B': 1},
            'B': {'C': 1, 'A': 1},
            'C': {'A': 1}
        }
        request = {
            'source': 'A',
            'destination': 'C',
            'max_travel_time': 5,
            'priority': 1
        }
        route = find_optimal_route(cyclic_graph, request)
        self.assertIsNotNone(route)
        self.assertEqual(route[0], 'A')
        self.assertEqual(route[-1], 'C')

    def test_multiple_valid_paths(self):
        # Graph with multiple valid paths
        multi_path_graph = {
            'A': {'B': 1, 'C': 1},
            'B': {'D': 1},
            'C': {'D': 1},
            'D': {}
        }
        request = {
            'source': 'A',
            'destination': 'D',
            'max_travel_time': 5,
            'priority': 1
        }
        route = find_optimal_route(multi_path_graph, request)
        self.assertIsNotNone(route)
        self.assertEqual(route[0], 'A')
        self.assertEqual(route[-1], 'D')
        self.assertLessEqual(len(route), 4)  # Should take shortest path in terms of hops

if __name__ == '__main__':
    unittest.main()