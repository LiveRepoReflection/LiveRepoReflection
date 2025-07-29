import unittest
from byzantine_paxos.byzantine_paxos import ByzantinePaxosSimulator

class TestByzantinePaxos(unittest.TestCase):
    def test_honest_consensus(self):
        n = 4
        f = 1
        proposals = [
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3]
        ]
        byzantine_nodes = set()
        simulator = ByzantinePaxosSimulator(n, f, proposals, byzantine_nodes)
        commitments = simulator.run()
        
        for slot in range(3):
            committed_values = {commitments[i][slot] for i in range(n)}
            self.assertEqual(len(committed_values), 1, "All honest nodes should commit same value")

    def test_byzantine_attack(self):
        n = 4
        f = 1
        proposals = [
            [1, 1, 1],
            [1, 1, 1],
            [2, 2, 2],  # Byzantine node
            [1, 1, 1]
        ]
        byzantine_nodes = {2}
        simulator = ByzantinePaxosSimulator(n, f, proposals, byzantine_nodes)
        commitments = simulator.run()
        
        # Check if honest nodes agree despite Byzantine node
        honest_commitments = [commitments[i] for i in range(n) if i not in byzantine_nodes]
        for slot in range(3):
            values = {hc[slot] for hc in honest_commitments}
            self.assertEqual(len(values), 1, "Honest nodes should agree despite Byzantine node")

    def test_no_quorum(self):
        n = 7
        f = 2
        proposals = [
            [1]*5,
            [1]*5,
            [2]*5,  # Byzantine
            [3]*5,  # Byzantine
            [1]*5,
            [1]*5,
            [1]*5
        ]
        byzantine_nodes = {2, 3}
        simulator = ByzantinePaxosSimulator(n, f, proposals, byzantine_nodes)
        commitments = simulator.run()
        
        # With 2 Byzantine nodes, honest nodes should still reach consensus
        for slot in range(5):
            honest_values = {commitments[i][slot] for i in range(n) if i not in byzantine_nodes}
            self.assertEqual(len(honest_values), 1, "Honest majority should reach consensus")

    def test_message_delay(self):
        n = 4
        f = 1
        proposals = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],  # Byzantine but behaves honestly in this case
            [1, 1, 1]
        ]
        byzantine_nodes = {2}
        simulator = ByzantinePaxosSimulator(n, f, proposals, byzantine_nodes)
        commitments = simulator.run()
        
        # Even with potential message delays, should reach consensus
        for slot in range(3):
            committed_values = {commitments[i][slot] for i in range(n) if i != 2}
            self.assertEqual(len(committed_values), 1, "Should reach consensus despite delays")

    def test_edge_case_minimum_nodes(self):
        n = 4  # Minimum for f=1
        f = 1
        proposals = [
            [1],
            [1],
            [2],  # Byzantine
            [1]
        ]
        byzantine_nodes = {2}
        simulator = ByzantinePaxosSimulator(n, f, proposals, byzantine_nodes)
        commitments = simulator.run()
        
        honest_values = {commitments[i][0] for i in range(n) if i != 2}
        self.assertEqual(len(honest_values), 1, "Minimum node configuration should work")

if __name__ == '__main__':
    unittest.main()