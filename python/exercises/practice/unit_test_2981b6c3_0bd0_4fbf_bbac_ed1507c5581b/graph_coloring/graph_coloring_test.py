import unittest
import time
from graph_coloring.graph_coloring import color_graph

class DummyGraphNode:
    def __init__(self, node_id, neighbors):
        self._node_id = node_id
        self._neighbors = neighbors
        self._color = None
        self.retry_counter = 0

    def node_id(self):
        return self._node_id

    def get_neighbors(self):
        return self._neighbors

    def get_color(self):
        return self._color

    def set_color(self, color):
        if self._color is not None:
            return self._color == color
        # In a real scenario, a conflict check against neighbors would occur.
        # For our dummy implementation, assume that once a color is set, it is accepted.
        self._color = color
        return True

class DummyDistributedGraph:
    def __init__(self, graph_dict):
        # graph_dict is a mapping: node_id -> list of neighbor node_ids.
        self.nodes = {}
        for node_id, neighbors in graph_dict.items():
            self.nodes[node_id] = DummyGraphNode(node_id, neighbors)
        self.communication_count = 0

    def get_node(self, node_id):
        self.communication_count += 1
        return self.nodes[node_id]

    def all_node_ids(self):
        return list(self.nodes.keys())

    def num_nodes(self):
        return len(self.nodes)

class TestGraphColoring(unittest.TestCase):
    def test_triangle_graph(self):
        # Triangle graph: 0-1, 1-2, 0-2
        graph_dict = {
            0: [1, 2],
            1: [0, 2],
            2: [0, 1]
        }
        graph = DummyDistributedGraph(graph_dict)
        retry_limit = 3
        timeout = 5.0
        color_graph(graph, retry_limit, timeout)
        colors = {}
        for node_id in graph.all_node_ids():
            node = graph.get_node(node_id)
            self.assertIsNotNone(node.get_color(), f"Node {node_id} not colored")
            colors[node_id] = node.get_color()
        for node_id, neighbors in graph_dict.items():
            for neighbor in neighbors:
                self.assertNotEqual(colors[node_id], colors[neighbor],
                                    f"Nodes {node_id} and {neighbor} share the same color")

    def test_disconnected_graph(self):
        # Two disconnected components
        graph_dict = {
            0: [1],
            1: [0],
            2: [],
            3: []
        }
        graph = DummyDistributedGraph(graph_dict)
        retry_limit = 3
        timeout = 5.0
        color_graph(graph, retry_limit, timeout)
        colors = {}
        for node_id in graph.all_node_ids():
            node = graph.get_node(node_id)
            self.assertIsNotNone(node.get_color(), f"Node {node_id} not colored")
            colors[node_id] = node.get_color()
        self.assertNotEqual(colors[0], colors[1], "Nodes 0 and 1 share the same color")

    def test_single_node(self):
        # Graph with a single isolated node.
        graph_dict = {0: []}
        graph = DummyDistributedGraph(graph_dict)
        retry_limit = 3
        timeout = 5.0
        color_graph(graph, retry_limit, timeout)
        node = graph.get_node(0)
        self.assertIsNotNone(node.get_color(), "Single node not colored")

    def test_complete_graph(self):
        # Complete graph with 4 nodes.
        graph_dict = {
            0: [1, 2, 3],
            1: [0, 2, 3],
            2: [0, 1, 3],
            3: [0, 1, 2]
        }
        graph = DummyDistributedGraph(graph_dict)
        retry_limit = 3
        timeout = 5.0
        color_graph(graph, retry_limit, timeout)
        colors = {}
        for node_id in graph.all_node_ids():
            node = graph.get_node(node_id)
            self.assertIsNotNone(node.get_color(), f"Node {node_id} not colored")
            colors[node_id] = node.get_color()
        for node_id, neighbors in graph_dict.items():
            for neighbor in neighbors:
                self.assertNotEqual(colors[node_id], colors[neighbor],
                                    f"Nodes {node_id} and {neighbor} share the same color")

    def test_retry_behavior(self):
        # Simulate a node that fails color assignment on the first two attempts.
        class FaultyNode(DummyGraphNode):
            def set_color(self, color):
                if self.retry_counter < 2:
                    self.retry_counter += 1
                    return False
                return super().set_color(color)

        graph_dict = {
            0: [1],
            1: [0]
        }
        class CustomDistributedGraph(DummyDistributedGraph):
            def __init__(self, graph_dict):
                self.nodes = {}
                for node_id, neighbors in graph_dict.items():
                    if node_id == 0:
                        self.nodes[node_id] = FaultyNode(node_id, neighbors)
                    else:
                        self.nodes[node_id] = DummyGraphNode(node_id, neighbors)
                self.communication_count = 0

        graph = CustomDistributedGraph(graph_dict)
        retry_limit = 3
        timeout = 5.0
        color_graph(graph, retry_limit, timeout)
        node0 = graph.get_node(0)
        node1 = graph.get_node(1)
        self.assertIsNotNone(node0.get_color(), "Faulty node 0 not colored")
        self.assertIsNotNone(node1.get_color(), "Node 1 not colored")
        self.assertNotEqual(node0.get_color(), node1.get_color(), "Nodes 0 and 1 share the same color")

    def test_timeout(self):
        # Test that the function respects the timeout by simulating slow network responses.
        class SlowNode(DummyGraphNode):
            def get_neighbors(self):
                time.sleep(0.01)
                return self._neighbors

        class SlowDistributedGraph(DummyDistributedGraph):
            def __init__(self, graph_dict):
                self.nodes = {}
                for node_id, neighbors in graph_dict.items():
                    self.nodes[node_id] = SlowNode(node_id, neighbors)
                self.communication_count = 0

        graph_dict = {
            0: [1],
            1: [0, 2],
            2: [1]
        }
        graph = SlowDistributedGraph(graph_dict)
        retry_limit = 3
        timeout = 2.0
        start_time = time.time()
        color_graph(graph, retry_limit, timeout)
        elapsed = time.time() - start_time
        self.assertLessEqual(elapsed, timeout + 1.0, f"Function exceeded timeout limit: {elapsed} seconds")
        colors = {}
        for node_id in graph.all_node_ids():
            node = graph.get_node(node_id)
            self.assertIsNotNone(node.get_color(), f"Node {node_id} not colored")
            colors[node_id] = node.get_color()
        for node_id, neighbors in graph_dict.items():
            for neighbor in neighbors:
                self.assertNotEqual(colors[node_id], colors[neighbor],
                                    f"Nodes {node_id} and {neighbor} share the same color")

if __name__ == '__main__':
    unittest.main()