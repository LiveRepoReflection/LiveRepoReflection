import unittest
import math

from dao_voting import determine_proposal_outcome

class TestDAOVoting(unittest.TestCase):
    def test_valid_votes(self):
        # Participants: (participant_id, reputation, public_key, private_key)
        participants = [
            (0, 100, "pub0", "priv0"),
            (1, 225, "pub1", "priv1"),
            (2, 400, "pub2", "priv2"),
        ]
        # For these tests, assume that a valid signature for a vote is "sig{voter_id}"
        votes = [
            (1, 0, "YES", "sig0"),
            (1, 1, "YES", "sig1"),
            (1, 2, "NO", "sig2"),
        ]
        # Weights: sqrt(100)=10, sqrt(225)=15, sqrt(400)=20 so YES sum = 25, NO sum = 20.
        # Outcome should be True.
        outcome = determine_proposal_outcome(participants, votes, 1)
        self.assertTrue(outcome)

    def test_duplicate_votes(self):
        participants = [
            (0, 100, "pub0", "priv0"),
            (1, 100, "pub1", "priv1"),
        ]
        votes = [
            (2, 0, "YES", "sig0"),
            (2, 0, "NO", "sig0_dup"),
            (2, 1, "NO", "sig1"),
        ]
        # Only first vote of participant 0 counts.
        # Weights: sqrt(100)=10 from each participant so YES = 10, NO = 10.
        # Outcome should be False as YES is not strictly greater.
        outcome = determine_proposal_outcome(participants, votes, 2)
        self.assertFalse(outcome)

    def test_invalid_signature(self):
        participants = [
            (0, 100, "pub0", "priv0"),
            (1, 225, "pub1", "priv1"),
        ]
        votes = [
            (3, 0, "YES", "sig0"),
            (3, 1, "YES", "invalid_signature"),
        ]
        # Only participant 0's vote is valid.
        # Weight: sqrt(100)=10, outcome should be True.
        outcome = determine_proposal_outcome(participants, votes, 3)
        self.assertTrue(outcome)

    def test_zero_reputation(self):
        participants = [
            (0, 0, "pub0", "priv0"),
            (1, 100, "pub1", "priv1"),
        ]
        votes = [
            (4, 0, "YES", "sig0"),
            (4, 1, "NO", "sig1"),
        ]
        # Participant 0 contributes sqrt(0)=0; participant 1 contributes sqrt(100)=10.
        # NO total = 10 vs YES total = 0, outcome should be False.
        outcome = determine_proposal_outcome(participants, votes, 4)
        self.assertFalse(outcome)

    def test_tie_outcome(self):
        participants = [
            (0, 100, "pub0", "priv0"),
            (1, 100, "pub1", "priv1"),
        ]
        votes = [
            (5, 0, "YES", "sig0"),
            (5, 1, "NO", "sig1"),
        ]
        # Both contribute sqrt(100)=10, so tie results in outcome False.
        outcome = determine_proposal_outcome(participants, votes, 5)
        self.assertFalse(outcome)

    def test_multiple_proposals(self):
        participants = [
            (0, 225, "pub0", "priv0"),
            (1, 225, "pub1", "priv1"),
            (2, 225, "pub2", "priv2"),
            (3, 225, "pub3", "priv3"),
        ]
        # Proposal 6: two YES and two NO votes leads to tie.
        votes = [
            (6, 0, "YES", "sig0"),
            (6, 1, "YES", "sig1"),
            (6, 2, "NO", "sig2"),
            (6, 3, "NO", "sig3"),
        ]
        outcome = determine_proposal_outcome(participants, votes, 6)
        self.assertFalse(outcome)

        # Proposal 7: three YES votes vs one NO vote.
        votes = [
            (7, 0, "YES", "sig0"),
            (7, 1, "YES", "sig1"),
            (7, 2, "YES", "sig2"),
            (7, 3, "NO", "sig3"),
        ]
        # Each participant weight is sqrt(225)=15; YES total = 45, NO total = 15.
        outcome = determine_proposal_outcome(participants, votes, 7)
        self.assertTrue(outcome)

    def test_large_number_of_participants(self):
        # Simulate a larger group of participants.
        participants = []
        votes = []
        proposal_id = 8
        num_participants = 100
        for i in range(num_participants):
            # Assign reputation as (i+1)*10 to introduce variety.
            participants.append((i, (i+1)*10, f"pub{i}", f"priv{i}"))
            # Valid signature assumed as "sig{i}".
            vote_decision = "YES" if i % 2 == 0 else "NO"
            votes.append((proposal_id, i, vote_decision, f"sig{i}"))
        
        # Calculate expected totals using quadratic weighting.
        yes_total = sum(math.sqrt((i+1)*10) for i in range(num_participants) if i % 2 == 0)
        no_total = sum(math.sqrt((i+1)*10) for i in range(num_participants) if i % 2 == 1)
        expected_outcome = yes_total > no_total
        outcome = determine_proposal_outcome(participants, votes, proposal_id)
        self.assertEqual(outcome, expected_outcome)

if __name__ == '__main__':
    unittest.main()