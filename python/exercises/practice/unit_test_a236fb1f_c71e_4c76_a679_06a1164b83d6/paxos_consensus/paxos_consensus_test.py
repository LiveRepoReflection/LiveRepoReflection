import unittest
import random
from paxos_consensus import paxos_simulation

class TestPaxosConsensus(unittest.TestCase):
    def setUp(self):
        # Ensure determinism by setting a fixed seed
        random.seed(42)

    def test_single_proposal_no_failures(self):
        # 3 nodes, single proposal. Expect consensus with exactly that value.
        N = 3
        proposals = [(0, 'value1')]
        agreed_value = paxos_simulation(N, proposals, failure_rate=0.0, message_loss_rate=0.0)
        self.assertEqual(agreed_value, 'value1')

    def test_multiple_proposals_no_failures(self):
        # 5 nodes, multiple proposals, no failures or message loss.
        N = 5
        proposals = [(0, 'A'), (1, 'B'), (2, 'C')]
        agreed_value = paxos_simulation(N, proposals, failure_rate=0.0, message_loss_rate=0.0)
        # The consensus value should be one of the proposed ones.
        self.assertIn(agreed_value, ['A', 'B', 'C'])

    def test_with_failures_and_losses(self):
        # 7 nodes, simulation with some node failures and message losses.
        N = 7
        proposals = [(0, 100), (2, 200), (4, 300)]
        agreed_value = paxos_simulation(N, proposals, failure_rate=0.2, message_loss_rate=0.1)
        # If consensus is reached, the agreed value must be one of the proposals.
        if agreed_value is not None:
            self.assertIn(agreed_value, [100, 200, 300])
        else:
            # It is acceptable for the simulation to fail to reach consensus in high failure scenarios.
            self.assertIsNone(agreed_value)

    def test_no_majority_due_to_failures(self):
        # 3 nodes with high failure rate to simulate inability to reach majority.
        N = 3
        proposals = [(0, 'X'), (1, 'Y')]
        agreed_value = paxos_simulation(N, proposals, failure_rate=0.9, message_loss_rate=0.0)
        self.assertIsNone(agreed_value)

    def test_deterministic_outcome(self):
        # Check that with a fixed random seed the outcome remains consistent across runs.
        N = 5
        proposals = [(0, 'Alpha'), (1, 'Beta')]
        value1 = paxos_simulation(N, proposals, failure_rate=0.1, message_loss_rate=0.1)
        random.seed(42)
        value2 = paxos_simulation(N, proposals, failure_rate=0.1, message_loss_rate=0.1)
        self.assertEqual(value1, value2)

if __name__ == '__main__':
    unittest.main()