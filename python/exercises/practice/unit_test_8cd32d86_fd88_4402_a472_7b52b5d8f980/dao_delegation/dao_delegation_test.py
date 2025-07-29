import math
import unittest

from dao_delegation import aggregate_votes

class TestAggregateVotes(unittest.TestCase):
    def test_valid_delegations(self):
        token_balances = {
            "A": 100,
            "B": 50,
            "C": 20
        }
        delegations = {
            "A": "C",
            "B": "C"
        }
        delegation_threshold = 10
        proposal_id = 1

        # Expected:
        # "A": base = 100 (even though A delegated, base remains)
        # "B": base = 50
        # "C": base 20 + delegation from A: int(sqrt(100)) = 10 + delegation from B: int(sqrt(50)) = 7
        expected = {
            "A": 100,
            "B": 50,
            "C": 20 + 10 + 7
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_self_delegation(self):
        token_balances = {
            "A": 100,
            "B": 50
        }
        delegations = {
            "A": "A",
            "B": "A"
        }
        delegation_threshold = 10
        proposal_id = 2

        # Self delegation ("A"->"A") is invalid. So only base tokens count.
        expected = {
            "A": 100,
            "B": 50
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_circular_delegation(self):
        token_balances = {
            "A": 100,
            "B": 100
        }
        delegations = {
            "A": "B",
            "B": "A"
        }
        delegation_threshold = 10
        proposal_id = 3

        # Cycle detected between A and B, so ignore delegations.
        expected = {
            "A": 100,
            "B": 100
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_delegation_threshold(self):
        token_balances = {
            "A": 5,
            "B": 20,
            "C": 40
        }
        delegations = {
            "A": "B",
            "C": "B"
        }
        delegation_threshold = 20
        proposal_id = 4

        # A's balance (5) is below the threshold and its delegation should be ignored.
        # C qualifies, so adds int(sqrt(40)) = 6 to B.
        expected = {
            "A": 5,
            "B": 20 + 6,
            "C": 40
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_non_existent_delegatee(self):
        token_balances = {
            "A": 100,
            "B": 50
        }
        delegations = {
            "A": "C"  # "C" does not exist in token_balances.
        }
        delegation_threshold = 10
        proposal_id = 5

        # Delegation ignored since delegatee "C" does not exist.
        expected = {
            "A": 100,
            "B": 50
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_chain_delegation(self):
        token_balances = {
            "A": 100,
            "B": 64,
            "C": 49
        }
        delegations = {
            "A": "B",
            "B": "C"
        }
        delegation_threshold = 10
        proposal_id = 6

        # Chain delegation: 
        # A delegates to B and qualifies: int(sqrt(100)) = 10 is added to B.
        # B delegates to C and qualifies: int(sqrt(64)) = 8 is added to C.
        # Note: delegation is not transitive beyond direct delegation.
        expected = {
            "A": 100,
            "B": 64 + 10,
            "C": 49 + 8
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_negative_values(self):
        token_balances = {
            "A": -100,
            "B": 50
        }
        delegations = {
            "A": "B"
        }
        # Negative token balance should revert to 0; negative threshold reverts to 0.
        delegation_threshold = -5
        proposal_id = 7

        # After reverting, A's token becomes 0, B remains 50.
        # Delegation from A qualifies because 0 >= 0, but int(sqrt(0)) is still 0.
        expected = {
            "A": 0,
            "B": 50
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

    def test_complex_chain_with_cycle_in_subchain(self):
        token_balances = {
            "A": 100,
            "B": 100,
            "C": 100,
            "D": 100
        }
        delegations = {
            "A": "B",  # A -> B
            "B": "C",  # B -> C
            "C": "B",  # C -> B creates a cycle between B and C
            "D": "C"   # D -> C, but C is in a cycle so should be ignored.
        }
        delegation_threshold = 10
        proposal_id = 8

        # Cycle detected between B and C: ignore all delegations involving B and C.
        # A delegates to B which is part of a cycle, so ignore.
        # D delegates to C, ignore.
        expected = {
            "A": 100,
            "B": 100,
            "C": 100,
            "D": 100
        }
        result = aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()