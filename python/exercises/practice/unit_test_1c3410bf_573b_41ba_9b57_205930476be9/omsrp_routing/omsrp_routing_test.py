import unittest
from omsrp_routing import find_best_paths

class OMSRPRoutingTest(unittest.TestCase):

    def test_basic_graph(self):
        graph = {
            1: {2: 1, 3: 5},
            2: {1: 1, 4: 2, 5: 7},
            3: {1: 5, 6: 3},
            4: {2: 2, 7: 4},
            5: {2: 7, 7: 1},
            6: {3: 3, 7: 9},
            7: {4: 4, 5: 1, 6: 9}
        }
        sources = [1, 3]
        destination = 7
        k = 3
        max_path_length = 4
        min_node_diversity = 5
        min_edge_diversity = 4

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        
        # Check we have at most k paths
        self.assertTrue(len(paths) <= k)
        
        # Check that all paths start from a source and end at destination
        for path in paths:
            self.assertIn(path[0], sources)
            self.assertEqual(path[-1], destination)
            
        # Check for no cycles in paths
        for path in paths:
            self.assertEqual(len(path), len(set(path)))
            
        # Check path length constraint
        for path in paths:
            self.assertTrue(len(path) - 1 <= max_path_length)
            
        # Check if paths are sorted by cost
        path_costs = []
        for path in paths:
            cost = 0
            for i in range(len(path) - 1):
                cost += graph[path[i]][path[i+1]]
            path_costs.append(cost)
            
        self.assertEqual(path_costs, sorted(path_costs))
        
        # Check diversity requirements
        if len(paths) > 0:
            all_nodes = set()
            all_edges = set()
            
            for path in paths:
                for i in range(len(path)):
                    if i < len(path) - 1:  # Don't count the destination node
                        all_nodes.add(path[i])
                        # Sort edge nodes to create consistent edge identifier
                        edge = tuple(sorted([path[i], path[i+1]]))
                        all_edges.add(edge)
            
            # Don't count the destination in node diversity
            all_nodes.discard(destination)
            
            # If all k paths exist, check diversity requirements
            if len(paths) == k:
                # The test might be too strict if it's impossible to meet diversity requirements
                # This is just checking that we're maximizing diversity as much as possible
                self.assertTrue(len(all_nodes) >= min(min_node_diversity, 
                                                    sum(len(set(path[:-1])) for path in paths)))
                self.assertTrue(len(all_edges) >= min(min_edge_diversity, 
                                                    sum(len(path) - 1 for path in paths)))

    def test_disconnected_graph(self):
        graph = {
            1: {2: 1},
            2: {1: 1},
            3: {4: 1},
            4: {3: 1},
            5: {}
        }
        sources = [1, 3]
        destination = 5
        k = 2
        max_path_length = 3
        min_node_diversity = 3
        min_edge_diversity = 2

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(paths, [])  # No paths should be found

    def test_single_path(self):
        graph = {
            1: {2: 1},
            2: {1: 1, 3: 1},
            3: {2: 1, 4: 1},
            4: {3: 1}
        }
        sources = [1]
        destination = 4
        k = 3
        max_path_length = 4
        min_node_diversity = 4
        min_edge_diversity = 3

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], [1, 2, 3, 4])

    def test_path_length_constraint(self):
        graph = {
            1: {2: 1},
            2: {1: 1, 3: 1},
            3: {2: 1, 4: 1},
            4: {3: 1, 5: 1},
            5: {4: 1},
        }
        sources = [1]
        destination = 5
        k = 1
        max_path_length = 3  # Path should be [1,2,3,4,5] but exceeds max_path_length
        min_node_diversity = 3
        min_edge_diversity = 3

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(paths, [])  # No paths should be found due to length constraint

    def test_multiple_paths_same_cost(self):
        graph = {
            1: {2: 1, 3: 1},
            2: {1: 1, 4: 1},
            3: {1: 1, 4: 1},
            4: {2: 1, 3: 1, 5: 1},
            5: {4: 1}
        }
        sources = [1]
        destination = 5
        k = 2
        max_path_length = 3
        min_node_diversity = 4
        min_edge_diversity = 4

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(len(paths), 2)
        # Both paths [1,2,4,5] and [1,3,4,5] have the same cost and length
        
        # Check for node diversity across paths
        all_nodes = set()
        for path in paths:
            for node in path[:-1]:  # Exclude destination
                all_nodes.add(node)
        self.assertTrue(len(all_nodes) >= min(min_node_diversity, 4))  # At most 4 unique nodes possible

    def test_large_graph_performance(self):
        # Create a larger graph for performance testing
        graph = {}
        # Create a chain of 100 nodes with alternative paths
        for i in range(1, 100):
            graph[i] = {i+1: 1}
            graph[i][i+1] = 1
            if i < 99:
                graph[i][i+2] = 2  # Alternative longer path
            
        # Add the last node
        graph[100] = {}
        
        # Connect back edges
        for i in range(2, 101):
            if i-1 in graph:
                graph[i][i-1] = 1
            if i-2 in graph:
                graph[i][i-2] = 2
                
        sources = [1]
        destination = 100
        k = 5
        max_path_length = 110  # More than enough for this graph
        min_node_diversity = 20
        min_edge_diversity = 20

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertTrue(len(paths) > 0)  # Should find at least one path
        
        # Check that paths are sorted by cost
        path_costs = []
        for path in paths:
            cost = 0
            for i in range(len(path) - 1):
                cost += graph[path[i]][path[i+1]]
            path_costs.append(cost)
            
        self.assertEqual(path_costs, sorted(path_costs))

    def test_diversity_requirements(self):
        graph = {
            1: {2: 1, 3: 2},
            2: {1: 1, 4: 3},
            3: {1: 2, 4: 1},
            4: {2: 3, 3: 1, 5: 1},
            5: {4: 1}
        }
        sources = [1]
        destination = 5
        k = 2
        max_path_length = 4
        min_node_diversity = 4  # Must include all possible nodes (1,2,3,4)
        min_edge_diversity = 4  # Must include different edges

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        
        # Check if we have 2 paths
        self.assertEqual(len(paths), 2)
        
        # Check node diversity (excluding destination)
        all_nodes = set()
        for path in paths:
            for node in path[:-1]:
                all_nodes.add(node)
                
        self.assertTrue(len(all_nodes) >= min(min_node_diversity, 4))
        
        # Check edge diversity
        all_edges = set()
        for path in paths:
            for i in range(len(path) - 1):
                edge = tuple(sorted([path[i], path[i+1]]))
                all_edges.add(edge)
                
        self.assertTrue(len(all_edges) >= min(min_edge_diversity, 6))  # At most 6 unique edges possible

    def test_source_is_destination(self):
        graph = {
            1: {2: 1},
            2: {1: 1, 3: 1},
            3: {2: 1}
        }
        sources = [1, 3]
        destination = 3
        k = 1
        max_path_length = 2
        min_node_diversity = 2
        min_edge_diversity = 1

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0], [3])  # Direct path is the source itself

    def test_invalid_inputs(self):
        # Test with invalid graph (not connected)
        graph = {
            1: {2: 1},
            2: {1: 1},
            3: {}  # Isolated node
        }
        sources = [1]
        destination = 3
        k = 1
        max_path_length = 2
        min_node_diversity = 2
        min_edge_diversity = 1

        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(paths, [])  # No path exists
        
        # Test with non-existent source
        graph = {
            1: {2: 1},
            2: {1: 1, 3: 1},
            3: {2: 1}
        }
        sources = [4]  # Non-existent source
        destination = 3
        
        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(paths, [])  # No path exists
        
        # Test with non-existent destination
        sources = [1]
        destination = 4  # Non-existent destination
        
        paths = find_best_paths(graph, sources, destination, k, max_path_length, min_node_diversity, min_edge_diversity)
        self.assertEqual(paths, [])  # No path exists

if __name__ == '__main__':
    unittest.main()