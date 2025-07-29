import unittest
from tx_commit import simulate_commit

class TxCommitTest(unittest.TestCase):
    def test_example(self):
        N = 3
        initial_votes = ["Commit", "Commit", "Abort"]
        rounds = [[1, 2], [2, 3]]
        coordinator_decision = ["Commit", "Commit"]
        expected = ["Commit", "Abort", "Abort"]
        result = simulate_commit(N, initial_votes, rounds, coordinator_decision)
        self.assertEqual(result, expected)

    def test_all_commit(self):
        N = 4
        initial_votes = ["Commit", "Commit", "Commit", "Commit"]
        rounds = [[1, 2, 3, 4]]
        coordinator_decision = ["Commit"]
        expected = ["Commit", "Commit", "Commit", "Commit"]
        result = simulate_commit(N, initial_votes, rounds, coordinator_decision)
        self.assertEqual(result, expected)

    def test_no_rounds(self):
        N = 3
        initial_votes = ["Commit", "Abort", "Commit"]
        rounds = []
        coordinator_decision = []
        expected = ["Uncertain", "Uncertain", "Uncertain"]
        result = simulate_commit(N, initial_votes, rounds, coordinator_decision)
        self.assertEqual(result, expected)

    def test_multi_round(self):
        N = 4
        initial_votes = ["Commit", "Commit", "Abort", "Commit"]
        rounds = [[1, 2, 4], [2, 3]]
        coordinator_decision = ["Commit", "Abort"]
        # Round 1: Nodes 1, 2, and 4 receive "Prepare".
        #   Their votes: "Commit", "Commit", "Commit" => result: "Commit"
        #   After round, nodes 1, 2, and 4 become Commit; node 3 remains Uncertain.
        # Round 2: Nodes 2 and 3 receive "Prepare".
        #   Their votes: node 2 (Commit) votes "Commit"; node 3 (Abort) votes "Abort" => result: "Abort"
        #   After round, node 2 updates to Abort and node 3 becomes Abort.
        # Final states: ["Commit", "Abort", "Abort", "Commit"]
        expected = ["Commit", "Abort", "Abort", "Commit"]
        result = simulate_commit(N, initial_votes, rounds, coordinator_decision)
        self.assertEqual(result, expected)

    def test_alternate_sequence(self):
        N = 5
        initial_votes = ["Commit", "Abort", "Commit", "Abort", "Commit"]
        rounds = [[1, 3, 5], [2, 3, 4]]
        coordinator_decision = ["Commit", "Abort"]
        # Round 1: Nodes 1, 3, and 5 receive "Prepare".
        #   Their votes: all "Commit" => decision "Commit"
        #   Nodes 1, 3, 5 become Commit; nodes 2 and 4 remain Uncertain.
        # Round 2: Nodes 2, 3, and 4 receive "Prepare".
        #   Their votes: node 2 ("Abort"), node 3 ("Commit"), node 4 ("Abort") => decision "Abort"
        #   Update: node 2 becomes Abort; node 3 (was Commit) now becomes Abort (since updates are allowed);
        #           node 4 becomes Abort.
        # Final states: ["Commit", "Abort", "Abort", "Abort", "Commit"]
        expected = ["Commit", "Abort", "Abort", "Abort", "Commit"]
        result = simulate_commit(N, initial_votes, rounds, coordinator_decision)
        self.assertEqual(result, expected)

    def test_repeated_participation(self):
        N = 3
        initial_votes = ["Commit", "Commit", "Commit"]
        rounds = [[1, 2], [2, 3], [1, 3]]
        coordinator_decision = ["Commit", "Abort", "Commit"]
        # Round 1: Nodes 1 and 2 are prepared with vote "Commit" and decision "Commit" => they become Commit.
        #         Node 3 remains Uncertain.
        # Round 2: Nodes 2 and 3 participate.
        #         Their votes: both "Commit" from initial_votes, but because node 2 participates again,
        #         and decision is "Abort", node 2 and node 3 become Abort.
        # Round 3: Nodes 1 and 3 participate.
        #         Node 1 was Commit and is not updated because it did not participate in a conflicting round.
        #         Node 3 remains Abort since nodes in the "Aborted" state must remain aborted.
        # Final result: ["Commit", "Abort", "Abort"]
        expected = ["Commit", "Abort", "Abort"]
        result = simulate_commit(N, initial_votes, rounds, coordinator_decision)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()