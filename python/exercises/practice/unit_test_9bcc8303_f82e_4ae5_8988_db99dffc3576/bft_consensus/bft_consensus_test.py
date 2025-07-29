import unittest
from bft_consensus import bft_consensus

class TestBftConsensus(unittest.TestCase):
    def test_all_honest_majority_commit(self):
        # n = 4, f = 0, threshold = (2*4+0)/3 = 8/3, need at least 3 votes.
        n = 4
        f = 0
        proposer_id = 1
        proposed_value = 1
        # All nodes receive the valid proposal of 1.
        received_values = [1, 1, 1, 1]
        # Test for a non-proposer node.
        result = bft_consensus(n, f, proposer_id, node_id=2, proposed_value=proposed_value, received_values=received_values)
        self.assertEqual(result, 1)

    def test_proposer_commit(self):
        # Test when the current node is the proposer.
        n = 4
        f = 0
        proposer_id = 0
        # For proposer, proposed_value is None.
        proposed_value = None
        received_values = [1, 1, 1, 1]
        result = bft_consensus(n, f, proposer_id, node_id=0, proposed_value=proposed_value, received_values=received_values)
        self.assertEqual(result, 1)

    def test_faulty_proposer_with_default_vote(self):
        # n = 5, f = 1, threshold = (2*5+1)/3 = 11/3 ~ 3.67, need at least 4 votes.
        n = 5
        f = 1
        proposer_id = 2
        proposed_value = 0
        # Simulate a faulty proposer by having one node send None (to be treated as default 0) 
        # and one node send an inconsistent value.
        received_values = [0, 0, None, 0, 1]
        result = bft_consensus(n, f, proposer_id, node_id=3, proposed_value=proposed_value, received_values=received_values)
        # With None converted to default 0, vote count for 0 becomes 4 and vote count for 1 is 1.
        self.assertEqual(result, 0)

    def test_insufficient_votes(self):
        # n = 6, f = 1, threshold = (2*6+1)/3 = 13/3 ~ 4.33, need at least 5 votes.
        n = 6
        f = 1
        proposer_id = 0
        proposed_value = 1
        # Received votes: valid 1's and others defaulting to 0.
        # index 0: 1, index 1: 1, index 2: None (default 0), index 3: 0, index 4: 0, index 5: 1.
        # Vote counts: 1 -> 3 votes; 0 -> 3 votes.
        received_values = [1, 1, None, 0, 0, 1]
        result = bft_consensus(n, f, proposer_id, node_id=4, proposed_value=proposed_value, received_values=received_values)
        self.assertIsNone(result)

    def test_honest_majority_with_faulty_nodes(self):
        # n = 7, f = 2, threshold = (2*7+2)/3 = 16/3 ~ 5.33, need at least 6 votes.
        n = 7
        f = 2
        proposer_id = 3
        proposed_value = 1
        # 6 nodes vote 1 and 1 node votes 0.
        received_values = [1, 1, 1, 1, 1, 1, 0]
        result = bft_consensus(n, f, proposer_id, node_id=5, proposed_value=proposed_value, received_values=received_values)
        self.assertEqual(result, 1)

    def test_all_abstain_defaults_to_zero(self):
        # All nodes receive None, which should default to 0.
        n = 5
        f = 1
        proposer_id = 4
        proposed_value = 0  # For non-proposer, proposed value is given.
        received_values = [None, None, None, None, None]
        result = bft_consensus(n, f, proposer_id, node_id=2, proposed_value=proposed_value, received_values=received_values)
        # All default to 0 results in a commit of 0.
        self.assertEqual(result, 0)

    def test_mixed_invalid_votes(self):
        # n = 6, f = 1, threshold = (2*6+1)/3 = 13/3 ~ 4.33, need at least 5 votes.
        n = 6
        f = 1
        proposer_id = 0
        proposed_value = 1
        # Some invalid values (e.g., 2 or -1) should be treated as invalid and default to 0.
        # Votes breakdown: index 0: 1, index 1: 2 (invalid -> 0), index 2: -1 (invalid -> 0),
        # index 3: None (default 0), index 4: 1, index 5: 1.
        received_values = [1, 2, -1, None, 1, 1]
        # Tally: value 1 -> 3 votes; default 0 -> 3 votes.
        result = bft_consensus(n, f, proposer_id, node_id=3, proposed_value=proposed_value, received_values=received_values)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()