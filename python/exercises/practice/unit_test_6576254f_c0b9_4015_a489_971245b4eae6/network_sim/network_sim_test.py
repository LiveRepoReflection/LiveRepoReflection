import unittest
from network_sim import simulate_information_spread

class TestNetworkSim(unittest.TestCase):
    def test_single_node(self):
        N = 1
        network = [[]]
        source = 0
        # Only one node is present, so no communication is needed.
        self.assertEqual(simulate_information_spread(N, network, source), 0)

    def test_linear_chain(self):
        N = 5
        network = [
            [1],       # Node 0 connected to Node 1
            [0, 2],    # Node 1 connected to Nodes 0 and 2
            [1, 3],    # Node 2 connected to Nodes 1 and 3
            [2, 4],    # Node 3 connected to Nodes 2 and 4
            [3]        # Node 4 connected to Node 3
        ]
        source = 0
        # Spread timeline: 
        # t=1: Node 1 infected
        # t=2: Node 2 infected
        # t=3: Node 3 infected
        # t=4: Node 4 infected
        self.assertEqual(simulate_information_spread(N, network, source), 4)

    def test_star_topology(self):
        N = 6
        network = [
            [1, 2, 3, 4, 5],  # Center node 0 connected to all others
            [0],
            [0],
            [0],
            [0],
            [0]
        ]
        source = 0
        # Spread timeline: 
        # t=1: All peripheral nodes (1,2,3,4,5) are infected.
        self.assertEqual(simulate_information_spread(N, network, source), 1)

    def test_cycle(self):
        N = 4
        network = [
            [1, 3],  # Node 0 connected to Nodes 1 and 3
            [0, 2],  # Node 1 connected to Nodes 0 and 2
            [1, 3],  # Node 2 connected to Nodes 1 and 3
            [2, 0]   # Node 3 connected to Nodes 2 and 0
        ]
        source = 1
        # Spread timeline:
        # t=1: Nodes 0 and 2 are infected.
        # t=2: Node 3 is infected.
        self.assertEqual(simulate_information_spread(N, network, source), 2)

    def test_disconnected(self):
        N = 4
        network = [
            [1],  # Component 1: Node 0 and Node 1
            [0],
            [3],  # Component 2: Node 2 and Node 3
            [2]
        ]
        source = 0
        # Nodes in the second component (Nodes 2 and 3) will never be infected.
        self.assertEqual(simulate_information_spread(N, network, source), -1)

    def test_complex_graph(self):
        N = 7
        network = [
            [1, 2],       # Node 0 connects to Nodes 1 and 2
            [0, 3, 4],    # Node 1 connects to Nodes 0, 3, 4
            [0, 4],       # Node 2 connects to Nodes 0, 4
            [1, 5],       # Node 3 connects to Nodes 1, 5
            [1, 2, 5, 6], # Node 4 connects to Nodes 1, 2, 5, 6
            [3, 4],       # Node 5 connects to Nodes 3, 4
            [4]           # Node 6 connects to Node 4
        ]
        source = 0
        # Spread timeline:
        # t=1: Nodes 1 and 2 infected.
        # t=2: From Node 1 infects Nodes 3 and 4; Node 2 tries infecting Node 4 (already infected).
        # t=3: From Node 3 infects Node 5, and from Node 4 infects Node 6.
        self.assertEqual(simulate_information_spread(N, network, source), 3)

    def test_large_network(self):
        # Create a large linear chain of nodes to test performance.
        N = 10000
        network = [[] for _ in range(N)]
        for i in range(N - 1):
            network[i].append(i + 1)
            network[i + 1].append(i)
        source = 0
        # In a linear chain, the infection takes N-1 time units to reach the end.
        self.assertEqual(simulate_information_spread(N, network, source), N - 1)

if __name__ == '__main__':
    unittest.main()