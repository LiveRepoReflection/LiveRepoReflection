import unittest
from optimal_flow import OptimalFlowNetwork

class TestOptimalFlowNetwork(unittest.TestCase):
    def setUp(self):
        # Setup network with 4 nodes, S=1, T=4.
        # Edges: (1,2)=5, (1,3)=10, (2,4)=5, (3,4)=10.
        N = 4
        S = 1
        T = 4
        edges = [
            (1, 2, 5),
            (1, 3, 10),
            (2, 4, 5),
            (3, 4, 10)
        ]
        # All nodes are initially online.
        statuses = {1: True, 2: True, 3: True, 4: True}
        self.network = OptimalFlowNetwork(N, S, T, edges, statuses)

    def test_initial_flow(self):
        # Expected max flow is 15: 5 via 1->2->4 and 10 via 1->3->4.
        flow = self.network.query_flow()
        self.assertEqual(flow, 15)

    def test_node_status_update(self):
        # Turn off node 2; only path 1->3->4 (flow=10) should remain.
        self.network.update_node(2, False)
        flow = self.network.query_flow()
        self.assertEqual(flow, 10)
        # Turn off node 3; no available path, flow should be 0.
        self.network.update_node(3, False)
        flow = self.network.query_flow()
        self.assertEqual(flow, 0)
        # Turn node 2 back on; with node 3 off, path 1->2->4 gives flow=5.
        self.network.update_node(2, True)
        flow = self.network.query_flow()
        self.assertEqual(flow, 5)
        # Bring node 3 online; both paths available, flow should return to 15.
        self.network.update_node(3, True)
        flow = self.network.query_flow()
        self.assertEqual(flow, 15)

    def test_capacity_update(self):
        # Increase capacity on edge (1,2) to 20; bottleneck at (2,4) remains: flow still 15.
        self.network.update_capacity(1, 2, 20)
        flow = self.network.query_flow()
        self.assertEqual(flow, 15)
        # Increase capacity on edge (2,4) to 15; now path 1->2->4 can carry 15 and path 1->3->4 10, total = 25.
        self.network.update_capacity(2, 4, 15)
        flow = self.network.query_flow()
        self.assertEqual(flow, 25)

    def test_series_of_updates(self):
        # Confirm initial flow.
        self.assertEqual(self.network.query_flow(), 15)
        # Disable node 3 and increase (2,4) capacity to 20.
        self.network.update_node(3, False)
        self.network.update_capacity(2, 4, 20)
        flow = self.network.query_flow()
        # Only path is 1->2->4 (limited by edge (1,2)=5) so flow = 5.
        self.assertEqual(flow, 5)
        # Re-enable node 3 and update (1,3) to 15.
        self.network.update_node(3, True)
        self.network.update_capacity(1, 3, 15)
        flow = self.network.query_flow()
        # Now 1->2->4 remains at 5 and 1->3->4 gives min(15,10)=10, total = 15.
        self.assertEqual(flow, 15)
        # Increase (3,4) capacity to 20; now 1->3->4 gives 15, total flow = 5 + 15 = 20.
        self.network.update_capacity(3, 4, 20)
        flow = self.network.query_flow()
        self.assertEqual(flow, 20)

    def test_disconnected_network(self):
        # Build a network where the sink is initially disconnected.
        N = 3
        S = 1
        T = 3
        edges = [
            (1, 2, 10)
        ]
        statuses = {1: True, 2: True, 3: True}
        nw = OptimalFlowNetwork(N, S, T, edges, statuses)
        flow = nw.query_flow()
        self.assertEqual(flow, 0)
        # Connect node 2 to node 3 with capacity 5.
        nw.update_capacity(2, 3, 5)
        flow = nw.query_flow()
        self.assertEqual(flow, 5)
        # Turn off node 2 so flow should drop to 0.
        nw.update_node(2, False)
        flow = nw.query_flow()
        self.assertEqual(flow, 0)

if __name__ == '__main__':
    unittest.main()