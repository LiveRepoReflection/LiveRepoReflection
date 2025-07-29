import unittest
from art_gallery import min_camera_cost

class ArtGalleryTest(unittest.TestCase):
    def test_simple_layout(self):
        graph = {
            0: [1],
            1: []
        }
        artwork_values = {
            0: [10],
            1: [20]
        }
        camera_costs = {
            0: 5,
            1: 3
        }
        # With a camera at node 0, the camera covers both node 0 and node 1.
        # Placing a camera only at node 1 does not cover node 0.
        # The minimum cost is 5.
        result = min_camera_cost(graph, artwork_values, camera_costs)
        self.assertEqual(result, 5)

    def test_disconnected_graph(self):
        graph = {
            0: [],
            1: [],
            2: []
        }
        artwork_values = {
            0: [10],
            1: [20, 30],
            2: [40]
        }
        camera_costs = {
            0: 5,
            1: 8,
            2: 7
        }
        # Each location is disconnected; a camera is needed at each node.
        # Total cost = 5 + 8 + 7 = 20.
        result = min_camera_cost(graph, artwork_values, camera_costs)
        self.assertEqual(result, 20)

    def test_cycle_graph(self):
        graph = {
            0: [1],
            1: [2],
            2: [0]
        }
        artwork_values = {
            0: [15],
            1: [25],
            2: [35]
        }
        camera_costs = {
            0: 4,
            1: 10,
            2: 6
        }
        # In a cycle graph, a camera placed at any node protects the entire cycle.
        # The minimum cost is 4 when placing the camera at node 0.
        result = min_camera_cost(graph, artwork_values, camera_costs)
        self.assertEqual(result, 4)

    def test_complex_graph(self):
        graph = {
            0: [1, 3],
            1: [2],
            2: [3],
            3: [4],
            4: []
        }
        artwork_values = {
            0: [10, 20],
            1: [30],
            2: [40],
            3: [],
            4: [50]
        }
        camera_costs = {
            0: 8,
            1: 5,
            2: 7,
            3: 3,
            4: 6
        }
        # Placing a camera at node 0 covers nodes 0, 1, 2, 3, and 4.
        # The minimum cost is therefore 8.
        result = min_camera_cost(graph, artwork_values, camera_costs)
        self.assertEqual(result, 8)

    def test_no_artwork(self):
        graph = {
            0: [1],
            1: [2],
            2: []
        }
        artwork_values = {
            0: [],
            1: [],
            2: []
        }
        camera_costs = {
            0: 5,
            1: 4,
            2: 3
        }
        # When there are no artworks at any location, no camera is needed.
        # The minimum cost is 0.
        result = min_camera_cost(graph, artwork_values, camera_costs)
        self.assertEqual(result, 0)

    def test_single_node_self_loop(self):
        graph = {
            0: [0]
        }
        artwork_values = {
            0: [100]
        }
        camera_costs = {
            0: 10
        }
        # Even with a self-loop, the only node requires a camera.
        # Minimum cost is 10.
        result = min_camera_cost(graph, artwork_values, camera_costs)
        self.assertEqual(result, 10)

if __name__ == '__main__':
    unittest.main()