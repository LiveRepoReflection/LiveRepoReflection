import unittest
from connected_subgraphs import decompose_graph

def is_highly_connected(subgraph, graph, k):
    for node in subgraph:
        # Count neighbors within the subgraph
        count = sum(1 for neighbor in graph.get(node, []) if neighbor in subgraph)
        if count < k:
            return False
    return True

def is_maximal(subgraph, graph, k):
    all_nodes = set(graph.keys())
    outside_nodes = all_nodes - subgraph
    for node in outside_nodes:
        candidate = subgraph | {node}
        if is_highly_connected(candidate, graph, k):
            return False
    return True

def check_sorted_output(output):
    # Check if the list is sorted (each set sorted as tuple)
    sorted_list = sorted([tuple(sorted(s)) for s in output])
    actual_list = [tuple(sorted(s)) for s in output]
    return actual_list == sorted_list

class ConnectedSubgraphsTest(unittest.TestCase):
    def test_empty_graph(self):
        graph = {}
        k = 1
        result = decompose_graph(graph, k)
        # For an empty graph, we expect an empty list as there are no subgraphs.
        self.assertEqual(result, [])

    def test_single_node(self):
        graph = {1: []}
        k = 0
        result = decompose_graph(graph, k)
        # For one node graph with k=0, the only maximal highly connected subgraph is {1}
        expected = [{1}]
        self.assertEqual(result, expected)

    def test_isolated_nodes(self):
        graph = {1: [], 2: []}
        k = 0
        result = decompose_graph(graph, k)
        # In a graph with isolated nodes and k=0, the maximal subgraph is the entire set.
        expected = [{1, 2}]
        self.assertEqual(result, expected)

    def test_sample_graph(self):
        # Example from problem description
        graph = {
            1: [2, 3, 4],
            2: [1, 3, 4, 5],
            3: [1, 2, 4],
            4: [1, 2, 3, 5],
            5: [2, 4]
        }
        k = 2
        result = decompose_graph(graph, k)
        # Verify each returned subgraph is highly connected and maximal
        self.assertTrue(check_sorted_output(result), "Output list is not sorted in ascending order")
        for subgraph in result:
            self.assertTrue(is_highly_connected(subgraph, graph, k), f"Subgraph {subgraph} is not highly connected with k={k}")
            self.assertTrue(is_maximal(subgraph, graph, k), f"Subgraph {subgraph} is not maximal")
        
    def test_clique_graph(self):
        # Create a clique of 5 nodes: every node is connected to every other node.
        nodes = [1, 2, 3, 4, 5]
        graph = {node: [n for n in nodes if n != node] for node in nodes}
        # For a clique, if k equals number of nodes-1, only the full clique is valid.
        k = 4
        result = decompose_graph(graph, k)
        # There should be one maximal subgraph: the whole clique.
        expected = [set(nodes)]
        self.assertEqual(result, expected)
        
    def test_nontrivial_graph(self):
        # Create a graph with two overlapping communities:
        # Community A: 1,2,3,4 fully connected; Community B: 3,4,5,6 fully connected.
        graph = {
            1: [2,3,4],
            2: [1,3,4],
            3: [1,2,4,5,6],
            4: [1,2,3,5,6],
            5: [3,4,6],
            6: [3,4,5]
        }
        k = 2
        result = decompose_graph(graph, k)
        self.assertTrue(check_sorted_output(result), "Output list is not sorted in ascending order")
        for subgraph in result:
            self.assertTrue(is_highly_connected(subgraph, graph, k), f"Subgraph {subgraph} is not highly connected with k={k}")
            self.assertTrue(is_maximal(subgraph, graph, k), f"Subgraph {subgraph} is not maximal")
            
    def test_high_k(self):
        # Graph where k is higher than any node's degree in the whole graph.
        graph = {
            1: [2],
            2: [1, 3],
            3: [2]
        }
        k = 2
        # No subgraph should satisfy: In any subgraph, some node will have degree less than 2.
        result = decompose_graph(graph, k)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()