import unittest
from time_network import find_shortest_paths

class TestTimeNetwork(unittest.TestCase):
    def test_single_source_simple(self):
        # Example provided in problem description.
        N = 4
        edges = [
            (0, 1, [(0, 10), (5, 20)]),   # If start at t = 0 -> cost 10; if started at t>=5 -> cost 20
            (0, 2, [(2, 5), (7, 15)]),     # If start before 2 -> unreachable; if 2<=t<7 -> cost 5; if t>=7 -> cost 15
            (1, 3, [(1, 30)])             # Always cost 30 if started at or after 1
        ]
        sources = [0]
        # For node 0: cost 0.
        # Node 1: take edge (0,1) at t = 0 => cost = 10.
        # Node 2: wait until t = 2, take edge (0,2) => cost = 5.
        # Node 3: path: 0 -> 1 (cost 10, arrival time 10) then (1,3) at t = 10 => cost = 30; total = 40.
        expected = [0, 10, 5, 40]
        result = find_shortest_paths(N, edges, sources)
        self.assertEqual(result, expected)

    def test_multiple_sources(self):
        # Graph with two sources.
        N = 5
        edges = [
            (0, 2, [(0, 5)]),              # cost 5 if started at t=0
            (1, 2, [(0, 3)]),              # cost 3 if started at t=0
            (2, 3, [(1, 10)]),             # must start at or after t=1 so if arrival at 2 is less than 1, wait till 1 (simulate cost remains 10 regardless)
            (3, 4, [(2, 2), (6, 4)]),       # if started between t=2 and t<6, cost 2; if started at t>=6, cost 4.
        ]
        # Sources are nodes 0 and 1.
        # For node 2, best is from source 1 with cost 3.
        # Node 3: from node 2 reached at time 3 (if source 1 used) then edge (2,3) cost 10 => total 3+10=13.
        # Node 4: starting at node 3 arrival 13 then edge (3,4) cost = since t>=6, cost = 4 => total 13+4=17.
        expected = [0, 0, 3, 13, 17]
        # Let the cost for nodes 0 and 1 be 0 as they are sources.
        result = find_shortest_paths(N, edges, [0, 1])
        self.assertEqual(result, expected)

    def test_unreachable_node(self):
        # Graph where one node is unreachable.
        N = 4
        edges = [
            (0, 1, [(0, 10)]),
            (1, 2, [(1, 5)]),
            # Node 3 is disconnected.
        ]
        sources = [0]
        # Node 0: 0, node 1: 10, node 2: 10+5=15, node 3: -1 (unreachable)
        expected = [0, 10, 15, -1]
        result = find_shortest_paths(N, edges, sources)
        self.assertEqual(result, expected)

    def test_time_dependency_wait(self):
        # Test where waiting to start an edge is beneficial because of time thresholds.
        N = 3
        edges = [
            # Edge from 0 to 1: if you start immediately at t=0, not allowed since t < 2 so unreachable.
            # You must wait until t=2 and then the cost is 4.
            (0, 1, [(2, 4), (5, 7)]),
            # Edge from 1 to 2: cost is constant once eligible.
            (1, 2, [(0, 3)])
        ]
        sources = [0]
        # For node 1, best is to wait until t=2 and then cost=4.
        # For node 2, arrival time at node 1 will be 2+4 = 6, then (1,2) cost=3.
        # Total cost for node 2 should be 4+3=7.
        expected = [0, 4, 7]
        result = find_shortest_paths(N, edges, sources)
        self.assertEqual(result, expected)

    def test_multiple_edges_same_pair(self):
        # Test multiple edges between same pair of nodes with different time-dependent costs.
        N = 3
        edges = [
            (0, 1, [(0, 10)]),
            (0, 1, [(0, 8), (3, 12)]),  # Parallel edge: if started at t=0, best cost is 8.
            (1, 2, [(1, 5)])
        ]
        sources = [0]
        # Best path: 0->1 with cost 8 (via second edge), then node 1 to 2 cost 5.
        # Total for node 2 becomes 8+5=13.
        expected = [0, 8, 13]
        result = find_shortest_paths(N, edges, sources)
        self.assertEqual(result, expected)

    def test_cycle_graph(self):
        # Graph contains a cycle.
        N = 4
        edges = [
            (0, 1, [(0, 2)]),
            (1, 2, [(0, 3)]),
            (2, 0, [(0, 1)]),  # Cycle between 0,1,2
            (1, 3, [(0, 4)])
        ]
        sources = [0]
        # Initial: 0=0.
        # From 0: to 1 cost 2.
        # Then from 1: to 2 cost 3, total 5; to 3 cost 4, total 6.
        # Cycle may try to reduce cost but cannot reduce 0 because starting cost already minimal.
        expected = [0, 2, 5, 6]
        result = find_shortest_paths(N, edges, sources)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()