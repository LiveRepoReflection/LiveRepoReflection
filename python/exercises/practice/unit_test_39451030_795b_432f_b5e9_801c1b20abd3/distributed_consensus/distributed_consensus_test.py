import unittest
from distributed_consensus import simulate_consensus

class DistributedConsensusTest(unittest.TestCase):

    def test_basic_consensus(self):
        # Scenario: 3 nodes, one node crashes in round 2.
        N = 3
        initial_values = [1, 2, 1]
        crash_pattern = [[], [1], []]
        max_rounds = 5
        # Expected: All non-crashed nodes eventually converge on 1.
        # Crashed nodes retain their value.
        expected = [1, 1, 1]
        result = simulate_consensus(N, initial_values, crash_pattern, max_rounds)
        self.assertEqual(result, expected)

    def test_tie_breaker_smallest(self):
        # Scenario: 4 nodes with distinct initial values.
        # In the first round, no majority exists so the smallest value is selected.
        N = 4
        initial_values = [3, 5, 2, 7]
        # No crashes
        crash_pattern = [[], [], []]
        max_rounds = 3
        # In round 1, proposals are [3,5,2,7] so all nodes choose min value = 2.
        expected = [2, 2, 2, 2]
        result = simulate_consensus(N, initial_values, crash_pattern, max_rounds)
        self.assertEqual(result, expected)

    def test_with_persistent_crashes(self):
        # Scenario: 4 nodes where some nodes crash permanently.
        N = 4
        initial_values = [1, 2, 3, 4]
        # Nodes 1 and 3 crash in round 1 and do not update afterwards.
        crash_pattern = [[1, 3], [], []]
        max_rounds = 4
        # Only nodes 0 and 2 update.
        # In round 1, active nodes: node0 has 1, node2 has 3, no majority exists,
        # so both adopt the smallest among received proposals (1).
        # Crashed nodes (nodes 1 and 3) retain their initial values.
        expected = [1, 2, 1, 4]
        result = simulate_consensus(N, initial_values, crash_pattern, max_rounds)
        self.assertEqual(result, expected)

    def test_max_rounds_limit(self):
        # Scenario: Use a max_rounds limit that might be reached before consensus among active nodes.
        # In this algorithm, the tie-breaking rule guarantees convergence among non-crashed nodes,
        # but we simulate a case with max_rounds set to a low value.
        N = 4
        initial_values = [4, 1, 3, 2]
        # No crashes.
        crash_pattern = [[], []]
        max_rounds = 1
        # With one round, nodes apply the rule only once.
        # In round 1, proposals are [4,1,3,2] so each node picks min value = 1 if no majority.
        expected = [1, 1, 1, 1]
        result = simulate_consensus(N, initial_values, crash_pattern, max_rounds)
        self.assertEqual(result, expected)

    def test_no_crashes_multiple_rounds(self):
        # Scenario: 5 nodes with a mix of initial values where consensus is reached after multiple rounds.
        N = 5
        initial_values = [10, 20, 5, 20, 15]
        # No node crashes.
        crash_pattern = [[], [], [], []]
        max_rounds = 10
        # Round 1: proposals are [10, 20, 5, 20, 15].
        # No majority exists (majority would require 3 of same value).
        # Thus, all nodes update to min(proposals)=5 in round 1.
        # Consensus is reached in one round.
        expected = [5, 5, 5, 5, 5]
        result = simulate_consensus(N, initial_values, crash_pattern, max_rounds)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()