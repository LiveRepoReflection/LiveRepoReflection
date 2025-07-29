import unittest
from edge_route import find_optimal_route

class EdgeRouteTest(unittest.TestCase):
    def test_basic_route(self):
        # Simple graph with one valid optimal route.
        graph = {
            1: [2, 3],
            2: [4],
            3: [4],
            4: []
        }
        node_resources = {
            1: (10, 20),
            2: (15, 25),
            3: (8, 15),
            4: (12, 18)
        }
        link_latencies = {
            (1, 2): 5,
            (1, 3): 3,
            (2, 4): 2,
            (3, 4): 4
        }
        stage_requirements = [(3, 5), (2, 4), (4, 6)]
        eligible_nodes = [
            [1, 2],  # Stage 1 can be executed on node 1 or 2
            [2, 3],  # Stage 2 can be executed on node 2 or 3
            [3, 4]   # Stage 3 can be executed on node 3 or 4
        ]
        deadline = 12
          
        # One optimal path is [1, 2, 4]: latency 5 + 2 = 7
        result = find_optimal_route(graph, node_resources, link_latencies,
                                    stage_requirements, eligible_nodes, deadline)
        self.assertEqual(result, [1, 2, 4])
    
    def test_no_valid_route_due_to_resources(self):
        # Graph and resource constraints are such that no node has enough resources for stage.
        graph = {
            1: [2],
            2: [3],
            3: []
        }
        node_resources = {
            1: (2, 2),
            2: (2, 2),
            3: (2, 2)
        }
        link_latencies = {
            (1, 2): 1,
            (2, 3): 1
        }
        stage_requirements = [(3, 3), (1, 1)]
        eligible_nodes = [
            [1, 2],   # Stage 1: no node has >= (3,3)
            [2, 3]
        ]
        deadline = 10
        
        result = find_optimal_route(graph, node_resources, link_latencies,
                                    stage_requirements, eligible_nodes, deadline)
        self.assertEqual(result, [])
    
    def test_no_valid_route_due_to_deadline(self):
        # Graph with valid resource allocations but no route within the deadline.
        graph = {
            1: [2, 3],
            2: [4],
            3: [4],
            4: []
        }
        node_resources = {
            1: (10, 10),
            2: (10, 10),
            3: (10, 10),
            4: (10, 10)
        }
        link_latencies = {
            (1, 2): 10,
            (1, 3): 10,
            (2, 4): 10,
            (3, 4): 10
        }
        stage_requirements = [(3, 3), (3, 3), (3, 3)]
        eligible_nodes = [
            [1, 2],
            [2, 3],
            [3, 4]
        ]
        deadline = 15  # All possible routes exceed this latency.
        
        result = find_optimal_route(graph, node_resources, link_latencies,
                                    stage_requirements, eligible_nodes, deadline)
        self.assertEqual(result, [])
    
    def test_multiple_valid_routes_with_tie_break(self):
        # Multiple valid routes, test that the minimum latency is returned.
        graph = {
            1: [2, 3],
            2: [4, 5],
            3: [5],
            4: [6],
            5: [6],
            6: []
        }
        node_resources = {
            1: (10, 10),
            2: (10, 10),
            3: (10, 10),
            4: (10, 10),
            5: (10, 10),
            6: (10, 10)
        }
        link_latencies = {
            (1, 2): 2,
            (1, 3): 2,
            (2, 4): 2,
            (2, 5): 3,
            (3, 5): 2,
            (4, 6): 2,
            (5, 6): 2
        }
        stage_requirements = [(2, 2), (2, 2), (2, 2)]
        eligible_nodes = [
            [1],      # Stage 1 only on 1
            [2, 3],   # Stage 2 on 2 or 3
            [4, 5, 6] # Stage 3 on 4, 5, or 6
        ]
        # Evaluate potential paths:
        # Option 1: [1, 2, 4] -> latency 2 + 2 = 4
        # Option 2: [1, 2, 5] -> latency 2 + 3 = 5
        # Option 3: [1, 3, 5] -> latency 2 + 2 = 4
        # Option 4: [1, 2, 6] or [1, 3, 6] require two hops from stage2 to stage3. Therefore, best is one hop.
        deadline = 10
        
        result = find_optimal_route(graph, node_resources, link_latencies,
                                    stage_requirements, eligible_nodes, deadline)
        # Expected result: one route with total latency equal to 4.
        self.assertTrue(result in ([1, 2, 4], [1, 3, 5]))
    
    def test_single_stage(self):
        # Only one stage so the route is a single node, and no latency is added.
        graph = {
            1: [2],
            2: []
        }
        node_resources = {
            1: (5, 5),
            2: (5, 5)
        }
        link_latencies = {
            (1, 2): 3
        }
        stage_requirements = [(3, 3)]
        eligible_nodes = [
            [1, 2]
        ]
        deadline = 5
        
        result = find_optimal_route(graph, node_resources, link_latencies,
                                    stage_requirements, eligible_nodes, deadline)
        # With one stage, either node is valid. Check that the returned node is eligible and has sufficient resources.
        self.assertIn(result, ([1], [2]))
        
if __name__ == '__main__':
    unittest.main()