import unittest
from network_flow_opt import maximize_stream_satisfaction

class MaximizeStreamSatisfactionTest(unittest.TestCase):

    def test_simple_full_satisfaction(self):
        # Network: 2 nodes, 1 edge, one stream that is fully satisfiable.
        N = 2
        M = 1
        edges = [(0, 1, 10)]
        p = [10, 10]
        K = 1
        streams = [(0, 1, 5)]
        # Expected: 5/5 * 100 = 100.00%
        result = maximize_stream_satisfaction(N, M, edges, p, K, streams)
        self.assertAlmostEqual(result, 100.00, places=2)

    def test_node_limitation(self):
        # Network: 3 nodes, 2 edges in a line.
        # The processing capacity at node 1 limits the flow.
        N = 3
        M = 2
        edges = [(0, 1, 5), (1, 2, 5)]
        p = [5, 3, 5]    # Node 1 can only process 3 units.
        K = 1
        streams = [(0, 2, 10)]
        # Expected: Only 3 can be delivered out of 10 => 30.00%
        result = maximize_stream_satisfaction(N, M, edges, p, K, streams)
        self.assertAlmostEqual(result, 30.00, places=2)

    def test_dual_route(self):
        # Network: 4 nodes forming two distinct paths from 0 to 3.
        N = 4
        M = 4
        edges = [(0, 1, 5), (1, 3, 5), (0, 2, 5), (2, 3, 5)]
        p = [10, 5, 5, 10]
        K = 2
        streams = [(0, 3, 5), (0, 3, 10)]
        # Total demand = 15, maximum flow possible = 10,
        # Thus satisfaction percentage = (10/15)*100 = 66.67%
        result = maximize_stream_satisfaction(N, M, edges, p, K, streams)
        self.assertAlmostEqual(result, 66.67, places=2)

    def test_disconnected(self):
        # Network: 3 nodes with only one edge; stream from node 0 to node 2 has no available path.
        N = 3
        M = 1
        edges = [(0, 1, 10)]
        p = [10, 10, 10]
        K = 1
        streams = [(0, 2, 5)]
        # Expected: Cannot deliver any flow => 0.00%
        result = maximize_stream_satisfaction(N, M, edges, p, K, streams)
        self.assertAlmostEqual(result, 0.00, places=2)

    def test_multiple_streams_shared_path(self):
        # Network: 3 nodes in a line with ample processing at node1, but edge capacities limit flows.
        N = 3
        M = 2
        edges = [(0, 1, 10), (1, 2, 10)]
        p = [10, 15, 10]
        # Two streams from node 0 to 2, each requesting 8 units. Total demand = 16.
        K = 2
        streams = [(0, 2, 8), (0, 2, 8)]
        # The edge (0,1) and (1,2) each admit at most 10 units.
        # Maximum deliverable flow is 10, so satisfaction = (10/16)*100 = 62.50%
        result = maximize_stream_satisfaction(N, M, edges, p, K, streams)
        self.assertAlmostEqual(result, 62.50, places=2)

    def test_rounding_precision(self):
        # Network: A single stream scenario where rounding is necessary.
        N = 3
        M = 2
        edges = [(0, 1, 7), (1, 2, 7)]
        p = [7, 10, 10]
        K = 1
        streams = [(0, 2, 13)]
        # Maximum deliverable flow is 7 due to edge capacities.
        # Satisfaction percentage = (7/13)*100 ≈ 53.84615... which rounds to 53.85%
        result = maximize_stream_satisfaction(N, M, edges, p, K, streams)
        self.assertAlmostEqual(result, 53.85, places=2)

if __name__ == '__main__':
    unittest.main()