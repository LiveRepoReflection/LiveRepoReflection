import unittest
from byzantine_delay import byzantine_agreement

class TestByzantineDelay(unittest.TestCase):
    def test_no_faults_single_round(self):
        # Scenario: 3 nodes, no faulty nodes, single round.
        N = 3
        F = 0
        V = 1
        delay_matrix = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ]
        R = 1
        faulty_nodes = set()
        result = byzantine_agreement(N, F, V, delay_matrix, R, faulty_nodes)
        # Expectation: All non-faulty nodes (all nodes in this case) decide on the commander's value.
        expected = [1, 1, 1]
        self.assertEqual(result, expected)

    def test_no_faults_multi_round(self):
        # Scenario: 4 nodes, no faulty nodes, multiple rounds.
        N = 4
        F = 0
        V = 0
        delay_matrix = [
            [0, 2, 1, 1],
            [1, 0, 2, 1],
            [1, 1, 0, 2],
            [2, 1, 1, 0]
        ]
        R = 2
        faulty_nodes = set()
        result = byzantine_agreement(N, F, V, delay_matrix, R, faulty_nodes)
        # With no faults and proper propagation, expect all nodes to decide on the initial value.
        expected = [0, 0, 0, 0]
        self.assertEqual(result, expected)

    def test_with_faulty_node(self):
        # Scenario: 5 nodes with one faulty node.
        # Faulty node may behave arbitrarily, but non-faulty nodes should reach consensus.
        N = 5
        F = 1
        V = 1
        delay_matrix = [
            [0, 1, 1, 1, 1],
            [1, 0, 1, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 1, 0, 1],
            [1, 1, 1, 1, 0]
        ]
        R = 2
        # Let's assume node 2 is faulty.
        faulty_nodes = {2}
        result = byzantine_agreement(N, F, V, delay_matrix, R, faulty_nodes)
        # Check output length and that non-faulty nodes agree on the same decision (either 0 or 1).
        self.assertEqual(len(result), N)
        non_faulty = [result[i] for i in range(N) if i not in faulty_nodes]
        self.assertTrue(all(decision in (0, 1) for decision in non_faulty))
        # All non-faulty nodes must agree on the same value.
        self.assertTrue(all(decision == non_faulty[0] for decision in non_faulty))

    def test_output_format(self):
        # Scenario to check that output is a list of integers of length N.
        N = 6
        F = 1
        V = 0
        delay_matrix = [
            [0, 1, 2, 1, 2, 1],
            [1, 0, 1, 2, 1, 2],
            [2, 1, 0, 1, 2, 1],
            [1, 2, 1, 0, 1, 2],
            [2, 1, 2, 1, 0, 1],
            [1, 2, 1, 2, 1, 0]
        ]
        R = 3
        faulty_nodes = {4}
        result = byzantine_agreement(N, F, V, delay_matrix, R, faulty_nodes)
        # Verify that the result is a list of integers (each 0 or 1) and matches the number of nodes.
        self.assertEqual(len(result), N)
        for decision in result:
            self.assertIn(decision, (0, 1))

if __name__ == '__main__':
    unittest.main()