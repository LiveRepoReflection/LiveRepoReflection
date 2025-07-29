import unittest
import time

# Import the consensus function from the project.
# It is assumed that the function is defined in dist_tx_consensus.py
from dist_tx_consensus import consensus

class DistTxConsensusTest(unittest.TestCase):
    def test_all_commit(self):
        # All involved nodes vote commit.
        N = 5
        involved_nodes = [0, 1, 2]
        coordinator_id = 0
        votes = {0: True, 1: True, 2: True}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertTrue(result, "Consensus should be True when all votes are commit.")

    def test_one_abort(self):
        # One node votes abort.
        N = 5
        involved_nodes = [1, 2, 3]
        coordinator_id = 1
        votes = {1: True, 2: False, 3: True}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertFalse(result, "Consensus should be False if any vote is abort.")

    def test_missing_vote_timeout(self):
        # One node does not vote (missing vote simulating timeout/failure).
        N = 6
        involved_nodes = [2, 3, 4]
        coordinator_id = 2
        # Only nodes 2 and 3 send their votes, node 4 fails to vote.
        votes = {2: True, 3: True}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertFalse(result, "Consensus should be False when a vote is missing (node failure).")

    def test_coordinator_vote_abort(self):
        # Coordinator votes abort even if others vote commit.
        N = 4
        involved_nodes = [0, 1, 2]
        coordinator_id = 0
        votes = {0: False, 1: True, 2: True}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertFalse(result, "Consensus should be False when the coordinator votes abort.")

    def test_out_of_order_votes(self):
        # Simulate out-of-order vote arrivals by shuffling the insertion order.
        N = 7
        involved_nodes = [3, 4, 5, 6]
        coordinator_id = 3
        votes_ordered = [(4, True), (6, True), (5, True), (3, True)]
        # Instead of relying on order, we use a dict which disregards order.
        votes = {node: vote for node, vote in votes_ordered}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertTrue(result, "Consensus should be True irrespective of the order of votes received.")

    def test_large_scale(self):
        # Test with a larger number of involved nodes all voting commit.
        N = 1000
        involved_nodes = list(range(100))
        coordinator_id = 0
        votes = {node: True for node in involved_nodes}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertTrue(result, "Consensus should be True for a large scale commit scenario.")

    def test_mixed_votes_with_failure(self):
        # Test with mixed voting results and simulate multiple missing votes.
        N = 50
        involved_nodes = [10, 20, 30, 40]
        coordinator_id = 10
        # Only two votes provided; missing votes should count as abort.
        votes = {10: True, 30: True}
        timeout = 1
        result = consensus(N, involved_nodes, coordinator_id, votes, timeout)
        self.assertFalse(result, "Consensus should be False when some nodes fail to vote due to timeout.")

if __name__ == '__main__':
    unittest.main()